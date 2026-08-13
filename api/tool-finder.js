// AI tool finder — recommends the best-fit HelpMeMarketing tool for a described need.
// Called from /ai-tools by the finder UI. Dependency-free (Node global fetch,
// no SDK, no package.json), matching the rest of /api.
//
// Requires the ANTHROPIC_API_KEY environment variable to be set in the Vercel
// project (Settings -> Environment Variables). Without it the endpoint returns
// a graceful "unavailable" response and the page falls back to showing every tool.

// Model: Haiku 4.5 is chosen deliberately for a public, high-volume, latency
// sensitive recommender (fast + a fraction of a cent per query). Swap to
// "claude-opus-5" here for maximum answer quality at higher cost/latency.
// Pinned to the dated snapshot: it is the exact id on the structured-outputs
// supported-models list, so output_config.format is guaranteed to be accepted.
var MODEL = 'claude-haiku-4-5-20251001';

// The tool catalog. Keep the URLs in sync with the cards on /ai-tools and the
// enum below. Adding a tool = add it here, add it to URL_ENUM, and add its card.
var TOOLS = [
  {
    url: '/tools/marketing-audit',
    name: 'AI Marketing Audit',
    when: 'They are unsure where to start, want an overall assessment, ask "is my marketing working", or want to benchmark their marketing maturity across channels.'
  },
  {
    url: '/ad-calculator',
    name: 'AdSpend Calculator',
    when: 'They have a question about ad budget or spend: how much to spend on ads, expected cost per lead (CPL), ROAS, or planning paid media budgets.'
  },
  {
    url: '/ad-set-calculator',
    name: 'Ad Set Calculator',
    when: 'They have a question about ad account structure or the Meta learning phase: how many ad sets to run, whether they have too many ad sets, which optimisation event (event, purchase, lead) their budget can support, or why their ad sets are stuck in learning limited.'
  },
  {
    url: '/seo-growth-os',
    name: 'SEO Growth OS',
    when: 'They care about SEO, organic traffic, Google rankings, being cited by AI search, "why isn\'t my site ranking", or technical/content SEO problems.'
  },
  {
    url: '/ad-calculator/benchmarks',
    name: 'Ad Spend Benchmarks',
    when: 'They want reference benchmark data: a good CPL, conversion rate, or LTV for DTC, SaaS, healthcare, or finance, or to compare their numbers to industry averages.'
  }
];

var URL_ENUM = TOOLS.map(function (t) { return t.url; }).concat(['none']);

var SYSTEM = [
  'You are the tool finder for HelpMeMarketing, a marketing agency.',
  'A visitor describes what they are trying to do. Recommend the single best-fit free tool from the catalog, and optionally one useful second tool.',
  '',
  'Catalog:',
  TOOLS.map(function (t) { return '- ' + t.name + ' (' + t.url + '): ' + t.when; }).join('\n'),
  '',
  'Rules:',
  '- primary_url must be the URL of the best-fit tool, or "none" if nothing in the catalog fits.',
  '- secondary_url is a genuinely useful second tool, or "none". Never repeat primary_url.',
  '- message: one or two short sentences, plain English, second person ("you"), telling them which tool to start with and why. No em-dashes. No hype words. If primary_url is "none", tell them to book a free audit and suggest they use the Contact page.',
  '- Base the choice only on the catalog. Do not invent tools or URLs.'
].join('\n');

// Best-effort per-instance rate limit (a warm lambda only). Real rate limiting
// across instances needs a shared store (e.g. Vercel KV); this just blunts abuse.
var HITS = {};
function rateLimited(ip) {
  var now = Date.now();
  var windowMs = 60000;
  var max = 20;
  var rec = HITS[ip];
  if (!rec || now - rec.start > windowMs) { HITS[ip] = { start: now, count: 1 }; return false; }
  rec.count += 1;
  return rec.count > max;
}

module.exports = async function (req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  if (req.method !== 'POST') {
    res.statusCode = 405;
    return res.end(JSON.stringify({ error: 'method_not_allowed' }));
  }

  var apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    // Graceful: the page falls back to showing all tools.
    console.error('[tool-finder] ANTHROPIC_API_KEY is not set');
    res.statusCode = 200;
    return res.end(JSON.stringify({ error: 'unavailable', primary_url: 'none', secondary_url: 'none', message: '' }));
  }

  // Body may arrive parsed (object) or raw (string) depending on runtime.
  var body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  var query = (body && typeof body.query === 'string') ? body.query.trim() : '';

  if (!query) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'empty_query' }));
  }
  if (query.length > 500) query = query.slice(0, 500);

  var ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (rateLimited(ip)) {
    res.statusCode = 429;
    return res.end(JSON.stringify({ error: 'rate_limited' }));
  }

  var controller = new AbortController();
  var timer = setTimeout(function () { controller.abort(); }, 12000);

  try {
    var apiRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 300,
        system: SYSTEM,
        messages: [{ role: 'user', content: query }],
        output_config: {
          format: {
            type: 'json_schema',
            schema: {
              type: 'object',
              properties: {
                primary_url: { type: 'string', enum: URL_ENUM },
                secondary_url: { type: 'string', enum: URL_ENUM },
                message: { type: 'string' }
              },
              required: ['primary_url', 'secondary_url', 'message'],
              additionalProperties: false
            }
          }
        }
      })
    });

    clearTimeout(timer);

    if (!apiRes.ok) {
      var errBody = '';
      try { errBody = await apiRes.text(); } catch (e) { errBody = '(body read failed)'; }
      console.error('[tool-finder] upstream ' + apiRes.status + ': ' + errBody.slice(0, 800));
      res.statusCode = 200;
      return res.end(JSON.stringify({ error: 'upstream', primary_url: 'none', secondary_url: 'none', message: '' }));
    }

    var data = await apiRes.json();
    var textBlock = (data.content || []).find(function (b) { return b.type === 'text'; });
    var parsed = {};
    try { parsed = JSON.parse(textBlock ? textBlock.text : '{}'); } catch (e) { parsed = {}; }

    var out = {
      primary_url: URL_ENUM.indexOf(parsed.primary_url) >= 0 ? parsed.primary_url : 'none',
      secondary_url: URL_ENUM.indexOf(parsed.secondary_url) >= 0 ? parsed.secondary_url : 'none',
      message: typeof parsed.message === 'string' ? parsed.message : ''
    };
    if (out.secondary_url === out.primary_url) out.secondary_url = 'none';

    res.statusCode = 200;
    return res.end(JSON.stringify(out));
  } catch (e) {
    clearTimeout(timer);
    console.error('[tool-finder] exception: ' + (e && e.message ? e.message : String(e)));
    res.statusCode = 200;
    return res.end(JSON.stringify({ error: 'exception', primary_url: 'none', secondary_url: 'none', message: '' }));
  }
};

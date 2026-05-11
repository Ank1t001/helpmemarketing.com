/* HelpMeMarketing — Marketing Maturity Audit content data
 * Source: HMM_Marketing_Audit_Content.md v1.0 (May 11, 2026)
 * V2.1 em-dash ban applied during build at CP2 (per blog template V2.1 rules).
 * Behaviour logic lives in /tools/marketing-audit.js (CP3). This file is data only.
 */
window.MARKETING_AUDIT_CONTENT = {
  tierOrder: ['foundational', 'growing', 'scaling', 'advanced'],

  tiers: {

    // ============================================================
    // FOUNDATIONAL — 0–30
    // ============================================================
    foundational: {
      name: 'Foundational',
      range: '0–30',
      descriptionHTML: `
<p class="audit-tier-diagnosis"><strong>You're running marketing on intuition, not infrastructure. Most of what's happening is reactive.</strong></p>

<p class="audit-tier-mirror"><em>Leads come in some months and not others, and you're not sure why. You spend on ads when business is slow and pull back when it's busy. You haven't really written down who your customer is. You'd know them when you see them.</em></p>

<h4>What's typical at this tier</h4>
<p>Most businesses we see start here, and most stay longer than they should. There's usually one channel that's quietly working (referrals, one ad campaign, an old SEO win) and a lot of guessing around it. Spend is reactive. Attribution is "how did you hear about us?" if it exists at all. The business is running, but the marketing isn't a system. It's a series of decisions made under pressure.</p>

<h4>The biggest gap</h4>
<p>You don't have a written ICP, a defined funnel, or measurement that drives decisions. Until those three exist, every channel will underperform because there's no way to tell what's working.</p>

<h4>What success looks like</h4>
<p>Moving to Growing isn't about more spend or more channels. It's about getting one channel working well enough that you can measure it, learn from it, and decide what to do next.</p>
      `.trim(),

      recommendationsHTML: `
<h4 class="audit-rec-primary-label">If you do nothing else</h4>
<div class="audit-rec-primary">
  <p><strong>Write a 1-page ICP doc this week.</strong> Four sections: who they are (industry, role, business stage), what triggers them to look for what you sell, what they buy instead today, and where they spend time online. One page. No template, no consultant. Just write it from your last five customers. This unlocks every other marketing decision you'll make for the next year. Without it, channel selection, ad copy, and landing pages are all guesswork.</p>
  <p class="audit-timeline"><em>Timeline: 2-3 hours of focused work this week.</em></p>
</div>

<h4 class="audit-rec-supporting-label">The 3 supporting actions</h4>
<ol class="audit-rec-supporting">
  <li>
    <p><strong>1. Pick one channel and commit for 90 days.</strong> Stop testing. Stop adding. Pick the channel where you have evidence your customers actually are (your existing customers; ask them). Run it consistently for 90 days. You can't diagnose what's working when you change the inputs every week.</p>
    <p class="audit-why"><em>Why it matters: Foundational businesses lose more to channel-switching than to running the wrong channel. 90 days is the minimum window to learn anything real.</em></p>
    <p class="audit-timeline"><em>Timeline: 90 days. Decision made this week.</em></p>
  </li>
  <li>
    <p><strong>2. Send paid traffic to a dedicated landing page, not your homepage.</strong> If you're running any paid ads, build one landing page for the campaign. Doesn't have to be fancy. Carrd, Webflow, or even a single page on your existing site works. One headline that matches the ad, three benefits, social proof, one form. Sending paid traffic to a homepage is the most expensive mistake at this tier.</p>
    <p class="audit-why"><em>Why it matters: Homepages are designed for branded traffic that already knows you. Paid traffic doesn't. The conversion gap is usually 3-5x.</em></p>
    <p class="audit-timeline"><em>Timeline: 1-2 days to build. Use Carrd ($19/yr) if you don't have a website builder you trust.</em></p>
  </li>
  <li>
    <p><strong>3. Set up GA4 properly and check it weekly, even briefly.</strong> If you don't have GA4, install it this week. If you have it but never look at it, set a recurring 15-minute weekly check on your calendar. You're not doing analysis. You're building the muscle of <em>looking</em>. The infrastructure is free; the habit is what's missing.</p>
    <p class="audit-why"><em>Why it matters: Every higher tier requires data fluency. You can't build that muscle later. You build it now by looking, even when you don't fully understand what you're seeing.</em></p>
    <p class="audit-timeline"><em>Timeline: GA4 install: 1 hour. Weekly check: 15 minutes, every week.</em></p>
  </li>
</ol>
      `.trim(),

      serviceMappingHTML: `
<h4>What good help looks like at this tier</h4>
<p><strong>Recommended service: Performance Marketing.</strong> Single channel, 90-day engagement.</p>

<p>At Foundational tier, the highest-leverage outside help is getting <em>one paid channel</em> set up and run properly while you build the operational muscles. Not a multi-channel program. Not a brand overhaul. One channel, usually Google Search or Meta, with the goals, tracking, and reporting cadence done right from day one.</p>

<p><strong>Engagement shape:</strong> 90-day initial sprint focused on a single channel. Strategy + setup + the first 60 days of active management. After 90 days, you decide whether to extend, switch the engagement model, or take it in-house.</p>

<p><strong>Why this scope at this tier:</strong></p>
<ul>
  <li>A Foundational business doesn't need ten things done. It needs one thing done well enough to learn from. Trying to do more usually means doing nothing well.</li>
  <li>90 days is the minimum window to learn anything real from a paid channel. Shorter engagements end before the data is interpretable.</li>
  <li>Single-channel focus means clean attribution. When everything's running through one channel, "what's working" is answerable.</li>
</ul>

<h4>In-house vs. partner: the honest contrast</h4>
<p><strong>In-house works if you have:</strong> A team member with real paid acquisition experience (not "they ran some Facebook ads once", actual time managing budgets and reading data), and at least 8-10 hours/week to dedicate to the channel.</p>

<p><strong>Partner works if you have:</strong> Budget for the channel but no internal expertise, no time to learn while running the business, or you've tried in-house and hit a ceiling you can't get past. Most Foundational businesses we work with are in this second category. They have the customer demand and the marketing budget but lack the operational time to build the function.</p>

<h4>What to avoid at this tier</h4>
<p><strong>Don't hire multiple specialists at once.</strong> A common Foundational mistake is hiring an SEO agency, a paid ads agency, and a content writer simultaneously, because everyone needs everything. Three uncoordinated engagements at this tier produce three half-finished programs, none of which generate enough signal to learn from. Pick one channel, get it right, then expand.</p>

<p><strong>Don't commit to long contracts.</strong> 12-month retainers at Foundational tier are a red flag. The agency benefits from the lock-in; you benefit from being able to walk away after 90 days if it isn't working. Insist on shorter terms or month-to-month after the initial sprint.</p>
      `.trim(),

      internalLinks: [
        { text: 'Read: How to build a marketing strategy from zero', href: '/blog/marketing-strategy-from-zero' },
        { text: 'Read: What marketing do you actually need at this stage?', href: '/blog/what-marketing-do-i-need' },
        { text: 'Explore: Performance marketing services', href: '/google-meta-ads' },
        { text: 'Start a conversation', href: '/contact' }
      ]
    },

    // ============================================================
    // GROWING — 31–55
    // ============================================================
    growing: {
      name: 'Growing',
      range: '31–55',
      descriptionHTML: `
<p class="audit-tier-diagnosis"><strong>You've built some marketing infrastructure, but it's working in pieces, not as a system.</strong></p>

<p class="audit-tier-mirror"><em>You have a written ICP, you're running on a couple of channels, and you check GA4 about once a month. You can roughly tell which channel works best, but when you try to explain why, the answer gets fuzzy. You know you should test more, measure more, follow up more. There's just never time.</em></p>

<h4>What's typical at this tier</h4>
<p>This is where most businesses with real marketing budgets land. There's a contact form, a basic email sequence, ads running on at least one platform. The pieces exist. What's missing is the connective tissue. The funnel isn't measured stage-by-stage, attribution stops at the channel level, and decisions still happen on instinct as often as on data. The business is past winging it, but not yet running a marketing operation.</p>

<h4>The biggest gap</h4>
<p>You're collecting data you don't act on. The infrastructure exists; the operating cadence doesn't. Until weekly review with real adjustments becomes routine, the next tier stays out of reach.</p>

<h4>What success looks like</h4>
<p>Moving to Scaling isn't about adding more channels or tools. It's about making the channels you already have measurable enough that you can confidently say which one to double down on, and which to cut.</p>
      `.trim(),

      recommendationsHTML: `
<h4 class="audit-rec-primary-label">If you do nothing else</h4>
<div class="audit-rec-primary">
  <p><strong>Install a weekly marketing review and never skip it.</strong> 60 minutes, same time every week, with one rule: every metric you look at has to produce a decision. Not "let's keep an eye on it"; an actual change to spend, creative, targeting, or process. If a metric never drives a decision in 8 weeks, remove it from the review. The infrastructure you've built doesn't compound until you build the cadence to act on it. This is the muscle that separates Growing from Scaling, and it costs nothing but discipline.</p>
  <p class="audit-timeline"><em>Timeline: First review scheduled this week. The muscle takes 90 days to feel natural.</em></p>
</div>

<h4 class="audit-rec-supporting-label">The 3 supporting actions</h4>
<ol class="audit-rec-supporting">
  <li>
    <p><strong>1. Tag every campaign with UTMs and audit your attribution gaps.</strong> Use Google's free Campaign URL Builder. Every paid campaign, every email, every social post that drives traffic: UTM tagged at the source. Then spend one hour in GA4 looking at where "(direct)" or "unassigned" traffic is coming from. That's your attribution gap, and it's almost always bigger than you think. You can't act on what you can't see.</p>
    <p class="audit-why"><em>Why it matters: At Growing tier, your channel-level attribution is probably 70-80% accurate. The missing 20-30% is where over- or under-spending decisions hide.</em></p>
    <p class="audit-timeline"><em>Timeline: 1 day to retag everything. 1 hour weekly to audit ongoing.</em></p>
  </li>
  <li>
    <p><strong>2. Build a basic conversion funnel and find your weakest stage.</strong> Map the actual stages: ad impression → click → landing page → form → qualified lead → customer. Get a real number on each stage's conversion rate. Most Growing businesses have one stage that's 3-5x worse than the others. That's the bottleneck, not the channel. Fix the bottleneck before adding spend or testing new channels.</p>
    <p class="audit-why"><em>Why it matters: Growing businesses spend on what's easiest to measure (top of funnel) instead of what's broken (middle of funnel). The bottleneck is usually a landing page or a form.</em></p>
    <p class="audit-timeline"><em>Timeline: 1 week to map and measure. Fix work depends on what you find.</em></p>
  </li>
  <li>
    <p><strong>3. Pick one experiment per month and run it through completion.</strong> Not three experiments in parallel. One, run to statistical sufficiency or 4 weeks, whichever comes first. Document what you tested, what changed, what you learned. The experimentation muscle is what compounds; the individual experiment results matter less than building the habit of testing systematically.</p>
    <p class="audit-why"><em>Why it matters: Growing businesses test sporadically and learn nothing because they never let an experiment run long enough or document what happened.</em></p>
    <p class="audit-timeline"><em>Timeline: One experiment cycle = 4 weeks. Pick this week's experiment now.</em></p>
  </li>
</ol>
      `.trim(),

      serviceMappingHTML: `
<h4>What good help looks like at this tier</h4>
<p><strong>Recommended services: Performance Marketing + Analytics/Attribution.</strong> Typically running in parallel.</p>

<p>At Growing tier, the gap isn't "we don't have marketing"; it's "we have marketing but it's not measurable enough to act on." The two services that address this directly are paid channel management (the inputs) and the analytics layer that makes spend decisions defensible (the visibility). Most Growing engagements at HMM run both in parallel because separating them at this tier leads to the same gap that brought the business to the audit: channels running without enough measurement to optimize them.</p>

<p><strong>Engagement shape (Performance Marketing):</strong> 90-day initial sprint expanding to ongoing management. At Growing, scope often includes 2-3 channels (not just one) because the business has signal across multiple platforms already. Monthly review cadence with quarterly strategic resets.</p>

<p><strong>Engagement shape (Analytics/Attribution):</strong> Project-based initial setup (4-6 weeks), then a lighter monthly retainer for dashboard maintenance and quarterly attribution audits. UTM hygiene, GA4 configuration, cross-platform reconciliation, and a single source-of-truth dashboard.</p>

<p><strong>Why this pairing at this tier:</strong></p>
<ul>
  <li>Running paid acquisition without proper attribution at Growing tier is the most common cause of plateau. Every Growing business we've worked with has had measurement gaps wider than they realized.</li>
  <li>Project-based analytics setup with lighter ongoing retainer keeps cost realistic. Analytics work compounds: you build the foundation once and maintain it cheaply.</li>
  <li>The two services compound. Better attribution drives smarter paid spend; smarter paid spend produces cleaner data to attribute.</li>
</ul>

<h4>In-house vs. partner: the honest contrast</h4>
<p><strong>In-house works if you have:</strong> A marketing lead with 2-3 years of paid acquisition experience, a designated analyst (full or part-time) who actually opens GA4 weekly, and at least 15-20 hours/week of combined team time on marketing operations.</p>

<p><strong>Partner works if you have:</strong> A marketing budget growing faster than your ability to hire senior talent, or a generalist marketing lead who's strong on strategy but doesn't have the analytics depth to build the measurement layer. The most common Growing-tier engagement we run is "your marketing lead + our analytics + our paid management" as a hybrid model. The internal lead keeps strategic ownership; we handle the operational depth.</p>

<h4>What to avoid at this tier</h4>
<p><strong>Don't hire three specialists who don't talk to each other.</strong> A Growing business with a paid ads agency, an SEO agency, and an email vendor running independently produces uncoordinated work and conflicting attribution claims. If you work with multiple partners, they need a coordination layer: either a senior internal marketing lead, or a single accountable partner that runs the program holistically.</p>

<p><strong>Don't ignore retention because no one's selling you a retention service.</strong> Most agencies (including ours, currently) lead with acquisition because that's where the obvious budget is. But at Growing tier, you have enough customer volume that retention math starts mattering. Build a basic lifecycle program in-house: welcome sequence, win-back, basic segmentation. It doesn't need an agency yet; it needs an owner. Most growing businesses can run a 3x improvement in retention value with one focused team member and Klaviyo or HubSpot. This is the work that compounds quietly while acquisition gets all the attention.</p>
      `.trim(),

      internalLinks: [
        { text: 'Read: The marketing KPIs that actually predict revenue', href: '/blog/marketing-kpis' },
        { text: 'Read: Why your Meta ROAS is lying to you', href: '/blog/meta-roas-attribution' },
        { text: 'Explore: Performance marketing services', href: '/google-meta-ads' },
        { text: 'Try: Estimate your channel performance', href: '/ad-calculator' }
      ]
    },

    // ============================================================
    // SCALING — 56–80
    // ============================================================
    scaling: {
      name: 'Scaling',
      range: '56–80',
      descriptionHTML: `
<p class="audit-tier-diagnosis"><strong>You're running a measurable marketing operation. The question now is which parts to scale and which to rebuild.</strong></p>

<p class="audit-tier-mirror"><em>You know your CAC by channel. UTM tags are on every campaign. Someone reviews performance weekly and changes get made. You've started running A/B tests, but only on the things that are easy to test. The ceiling you're hitting isn't a budget problem or a channel problem. It's that the next level of growth needs different muscles than the ones that got you here.</em></p>

<h4>What's typical at this tier</h4>
<p>Businesses at Scaling have figured out attribution at the channel level, built landing pages that convert, and run paid acquisition with discipline. The funnel is measured, the dashboards exist, the operating cadence is real. What's missing isn't infrastructure. It's experimentation muscle and cross-channel integration. Most businesses at this tier are running parallel programs that don't talk to each other: paid ads optimizing for last-click, SEO building authority, email sending offers. Each works. Together, they don't compound.</p>

<h4>The biggest gap</h4>
<p>You're optimizing within channels but not across them. The next tier requires treating the marketing program as one system, not five, and running real experiments on the parts that matter, not the parts that are easy to measure.</p>

<h4>What success looks like</h4>
<p>Moving to Advanced isn't about more sophistication. It's about integration: making channels reinforce each other, attribution see across them, and decisions weigh the whole system instead of one platform's report.</p>
      `.trim(),

      recommendationsHTML: `
<h4 class="audit-rec-primary-label">If you do nothing else</h4>
<div class="audit-rec-primary">
  <p><strong>Run a cross-channel attribution audit and name what you're double-counting.</strong> Pull the last 90 days of conversion data from each platform: Google Ads, Meta, GA4, your CRM. Add up the "conversions attributed to me" claims from each platform. The total is almost always 20-40% higher than your actual customer count. That's the double-counting problem. Sit down with your team and name which channels are getting credit they don't deserve, and which assist channels are getting none. Until you can see the system, you can't optimize the system.</p>
  <p class="audit-timeline"><em>Timeline: 1 week to pull and reconcile. The conversation it triggers takes longer, but it has to happen.</em></p>
</div>

<h4 class="audit-rec-supporting-label">The 3 supporting actions</h4>
<ol class="audit-rec-supporting">
  <li>
    <p><strong>1. Build a single source of truth dashboard outside any one ad platform.</strong> GA4 alone isn't enough. Looker Studio (free) or a paid tool like Funnel.io or Whatagraph. Pick one, build a dashboard that reports on the <em>business</em> not the <em>platforms</em>. Customer acquisition cost, lifetime value, revenue by channel, blended ROAS. The dashboard should answer "what should we do this week?" not "what did Google Ads say happened last week?" Most Scaling businesses have 5+ dashboards that contradict each other. One source of truth is non-negotiable.</p>
    <p class="audit-why"><em>Why it matters: Cross-channel decisions require cross-channel data. As long as the highest-fidelity dashboard lives inside a single ad platform, you'll keep over-investing in that platform.</em></p>
    <p class="audit-timeline"><em>Timeline: 2-4 weeks for a real implementation. Free tools cover most needs; paid tools save time.</em></p>
  </li>
  <li>
    <p><strong>2. Stop optimizing within channels and start optimizing across them.</strong> The Scaling failure pattern is paid teams optimizing CPL, SEO teams optimizing rankings, email teams optimizing open rates: none of them talking, all of them claiming credit. Pick one cross-channel motion to test this quarter: a retargeting program that uses email engagement to filter Meta audiences, an SEO content piece that powers a paid landing page, an email re-engagement campaign that follows up paid-ads non-converters. The point isn't the specific tactic. It's building the habit of asking "how do these channels reinforce each other?"</p>
    <p class="audit-why"><em>Why it matters: Within-channel optimization has diminishing returns at Scaling. Cross-channel multiplication is where the next 30-50% of efficiency lives.</em></p>
    <p class="audit-timeline"><em>Timeline: 4-8 weeks per cross-channel experiment. Start with one, do it well.</em></p>
  </li>
  <li>
    <p><strong>3. Run a quarterly portfolio review on your full marketing mix.</strong> Once a quarter, sit with the question: "If I had to cut 20% of marketing spend tomorrow, what would go and why?" The answer should be defensible without referring to platform reports. The exercise forces clarity on which programs are doing the work and which are running because no one's questioned them. Most Scaling businesses have 1-2 zombie programs eating budget without contributing. The portfolio review surfaces them.</p>
    <p class="audit-why"><em>Why it matters: At Scaling, the constraint shifts from "are we spending enough?" to "is every dollar earning its place?" The portfolio review is how you maintain spend discipline as the operation grows.</em></p>
    <p class="audit-timeline"><em>Timeline: 90-minute quarterly meeting. Decision-makers only, not the full team.</em></p>
  </li>
</ol>
      `.trim(),

      serviceMappingHTML: `
<h4>What good help looks like at this tier</h4>
<p><strong>Recommended services: Performance Marketing + Analytics/Attribution + Custom Dashboards.</strong> Typically running as an integrated program.</p>

<p>At Scaling tier, the engagement model shifts from "we do this for you" to "we run this layer of your marketing operation." The three services above aren't a bundle. They're the operational stack that makes cross-channel decisions possible. Most Scaling engagements at HMM run all three because the gaps that brought a Scaling business to the audit (cross-channel attribution, parallel programs that don't compound, dashboards that contradict each other) require integrated work, not separate engagements.</p>

<p><strong>Engagement shape (Performance Marketing):</strong> Ongoing channel management across 3-5 platforms (Google, Meta, LinkedIn, programmatic, etc.). Weekly optimization, monthly strategic reviews, quarterly portfolio resets. At Scaling, the deliverable isn't "ads running". It's "spend allocation defended with cross-channel data."</p>

<p><strong>Engagement shape (Analytics/Attribution):</strong> Continuous attribution work, not project-based. UTM governance, cross-platform reconciliation, regular audits of where attribution is breaking, and infrastructure work to close the gaps. This is the layer that makes the rest of the program defensible.</p>

<p><strong>Engagement shape (Custom Dashboards):</strong> Initial build (6-8 weeks for a real Scaling-tier dashboard), then ongoing iteration as the business evolves. Looker Studio for most, paid platforms (Funnel.io, Looker, Tableau) when the data volume or stakeholder count justifies it. The dashboard is the single source of truth: not a reporting deliverable, but the decision-making infrastructure.</p>

<p><strong>Why this stack at this tier:</strong></p>
<ul>
  <li>Cross-channel optimization is impossible without all three layers working together. Performance management without attribution is guessing; attribution without dashboards is data that no one looks at; dashboards without performance work is reporting on someone else's decisions.</li>
  <li>An integrated provider running all three eliminates the "whose data is right?" problem. The Scaling failure mode of three agencies arguing over conversion credit goes away when one team owns the measurement layer.</li>
  <li>The three services share strategic context. Decisions in one inform the others in real time: channel performance changes how attribution is read, which changes what dashboards prioritize, which changes how performance budget gets allocated.</li>
</ul>

<h4>In-house vs. partner: the honest contrast</h4>
<p><strong>In-house works if you have:</strong> A senior marketing leader (VP-level or strong director) who owns strategy, plus dedicated specialists for at least two of the three layers (paid acquisition, analytics, BI/dashboards), plus 30+ hours/week of combined team time on marketing operations. At Scaling, in-house is genuinely viable, but it usually requires more senior talent than businesses realize.</p>

<p><strong>Partner works if you have:</strong> Senior strategic ownership internally but operational depth gaps in one or more layers, or you've outgrown the "one agency per channel" model and need integration. The most common Scaling engagement at HMM is a partnership with an internal marketing leader who treats us as their operations and measurement team. They own strategy; we own execution and the data layer underneath it. The reverse, outsourcing strategy while keeping execution in-house, almost never works at this tier.</p>

<h4>What to avoid at this tier</h4>
<p><strong>Don't hire a specialist agency per channel without an integration layer.</strong> The Scaling failure pattern is one agency for Google, one for Meta, one for SEO, one for email: all running independently, all claiming credit for the same customers, all reporting in their own format. This produces the cross-channel attribution chaos that brought the business to the audit. If you work with channel specialists, you need someone (internal lead or accountable partner) holding the integration layer.</p>

<p><strong>Don't outsource the dashboard layer to whichever agency you happen to like best.</strong> The dashboard is the decision-making infrastructure for the entire program. It shouldn't live inside a channel agency's reporting tool. Either keep it in-house (with someone senior enough to own it) or assign it to the partner running the analytics/attribution work. The dashboard owns the truth; the agencies optimize against it. Inverting that relationship is how Scaling businesses lose control of their own marketing data.</p>

<p><strong>Don't ignore retention yet again.</strong> At Scaling tier, retention isn't optional. The unit economics depend on it. We still don't currently offer a dedicated lifecycle service (same admission as the Growing tier), but at Scaling the gap is bigger because the math matters more. If your CAC is climbing and your LTV is flat, no amount of acquisition optimization will fix that. Hire a lifecycle marketing specialist (in-house or contractor), or partner with a retention-specialized agency. Performance Marketing + Analytics + Dashboards is HMM's strongest contribution at this tier, but it's only half the system: the retention half belongs to someone, and at Scaling you need to name who.</p>
      `.trim(),

      internalLinks: [
        { text: 'Read: Why your Meta ROAS is lying to you', href: '/blog/meta-roas-attribution' },
        { text: 'Read: The marketing KPIs that actually predict revenue', href: '/blog/marketing-kpis' },
        { text: 'Explore: Analytics services', href: '/analytics' },
        { text: 'Talk to us about a custom dashboard build', href: '/contact' }
      ]
    },

    // ============================================================
    // ADVANCED — 81–100
    // ============================================================
    advanced: {
      name: 'Advanced',
      range: '81–100',
      descriptionHTML: `
<p class="audit-tier-diagnosis"><strong>You've built an integrated marketing program. The work now is compounding it, not adding to it.</strong></p>

<p class="audit-tier-mirror"><em>You can answer where any customer came from, what they did before buying, and how the channels worked together to get them there. Your team runs experiments on the things that move revenue, not the things that are easy to test. You've stopped adding tools and started removing them. The questions you're trying to answer now aren't "is marketing working". They're "where's the next 20% coming from."</em></p>

<h4>What's typical at this tier</h4>
<p>Businesses at Advanced are rare. Marketing operates as a system: paid acquisition, organic, lifecycle, and brand reinforce each other; attribution sees across channels; the operating cadence is tight enough that decisions happen in days, not quarters. The team is past collecting data and past acting on it. They're now compounding it. What separates Advanced from "very good" is that the program isn't just measured, it's predictive. You can model what a budget shift will do before you make it.</p>

<h4>The biggest gap</h4>
<p>The frontier at this tier isn't infrastructure or discipline. It's category position. The next ceiling is brand pull: turning marketing efficiency into market leadership, where customers find you before they search.</p>

<h4>What success looks like</h4>
<p>There's no clean tier above 81-100 in this audit, but there's a real one in the market. It's the businesses that don't just acquire customers efficiently. They're the default choice in their category before anyone clicks an ad.</p>
      `.trim(),

      recommendationsHTML: `
<h4 class="audit-rec-primary-label">If you do nothing else</h4>
<div class="audit-rec-primary">
  <p><strong>Build a 12-month brand investment plan separate from your performance marketing budget.</strong> Performance marketing has plateaued for you by definition; you've optimized it. The next 20% of growth lives in brand pull: customers arriving with intent because they already know you, not because they clicked an ad. Allocate 15-25% of total marketing spend to brand work that won't show up in last-click attribution: thought leadership, category-defining content, podcast and partnership presence, owned audience growth. Measure it by branded search volume and direct traffic, not by ROAS. Most Advanced businesses won't do this because the discomfort of un-attributable spend is real. The ones who do, compound past their competition.</p>
  <p class="audit-timeline"><em>Timeline: Plan built this quarter. Investment runs 12 months minimum before signal appears.</em></p>
</div>

<h4 class="audit-rec-supporting-label">The 3 supporting actions</h4>
<ol class="audit-rec-supporting">
  <li>
    <p><strong>1. Move from descriptive measurement to predictive modeling.</strong> Your dashboards tell you what happened. The next layer tells you what will happen. Build a media mix model (or buy one: Recast, Mixpanel, or in-house with a data scientist) that lets you simulate budget shifts before you make them. The point isn't perfect prediction; it's having a defensible answer to "what happens if we cut Meta by 30% next quarter?" before you actually cut Meta. Decision-making speed at Advanced shifts from data-informed to model-informed.</p>
    <p class="audit-why"><em>Why it matters: Advanced operations make budget decisions weekly. The ones who simulate first outperform the ones who learn through doing.</em></p>
    <p class="audit-timeline"><em>Timeline: 3-6 months to build or implement. Pays off across every budget cycle after that.</em></p>
  </li>
  <li>
    <p><strong>2. Audit your stack and remove what isn't compounding.</strong> Advanced marketing operations accumulate tools: every ICP iteration added a platform, every team change brought new preferences. Run a tool audit: list every paid tool, the workflow it serves, and the last time anyone used it for a decision that changed outcomes. Most Advanced stacks can lose 20-30% of their tools with no impact on results, and the savings fund the brand investment plan above. The signal of operational maturity at this tier isn't what you add. It's what you remove.</p>
    <p class="audit-why"><em>Why it matters: Tool sprawl is the silent tax on Advanced operations. The compounding effect of a leaner stack shows up in team velocity, not P&L line items.</em></p>
    <p class="audit-timeline"><em>Timeline: 2-4 weeks to audit. Cuts roll through the next renewal cycle.</em></p>
  </li>
  <li>
    <p><strong>3. Invest in the team layer, not the tool layer.</strong> At Advanced, the binding constraint is rarely budget or technology. It's the depth and seniority of the people running the program. Hire one strategist-level marketer who can think about the whole system, not three coordinators who can execute pieces of it. Or invest in moving your best people from execution to design. The recommendations above (predictive modeling, stack audit, brand plan) all require senior judgment that junior teams can't provide.</p>
    <p class="audit-why"><em>Why it matters: Tools and tactics commoditize. Strategic judgment doesn't. The Advanced businesses that compound past their tier are the ones that invested in people two years before they needed them.</em></p>
    <p class="audit-timeline"><em>Timeline: Hiring cycles run 60-120 days. Internal promotions are faster but require existing depth.</em></p>
  </li>
</ol>
      `.trim(),

      serviceMappingHTML: `
<h4>What good help looks like at this tier</h4>
<p><strong>Recommended services: selective engagement across Custom Dashboards + Analytics/Attribution + Custom Apps.</strong> Typically as specialized capability supplements, not full-function partnership.</p>

<p>At Advanced tier, the engagement model shifts again, from "we run this layer of your operation" (Scaling) to "we build specific things your internal team needs but doesn't have capacity or specialized depth for." Most Advanced engagements at HMM aren't comprehensive program management. They're project-shaped: purpose-built dashboards for specific business questions, attribution infrastructure rebuilds, internal marketing tools or custom apps that off-the-shelf platforms don't cover.</p>

<p><strong>Engagement shape (Custom Dashboards):</strong> Project-based builds for specific decision-making needs (executive-level mix modeling dashboards, cohort retention reporting, CAC/LTV ratio monitoring by segment). Typically 4-8 week builds with ongoing iteration as the business evolves. At Advanced, dashboards are domain-specific: generic reporting tools fail to answer the actual strategic questions the business is asking.</p>

<p><strong>Engagement shape (Analytics/Attribution):</strong> Specialized work: server-side tracking implementation, MMM (media mix modeling) builds in collaboration with internal data science teams, attribution rebuilds when platform changes (iOS, cookie deprecation, GA4 migrations) break existing infrastructure. Project-based with retainer support for ongoing maintenance.</p>

<p><strong>Engagement shape (Custom Apps):</strong> Internal tools that bridge gaps between platforms (campaign brief generators, automated reporting pipelines, custom CRM integrations, marketing operations tooling that doesn't exist as SaaS). 6-12 week build cycles. This is the service Advanced businesses underuse because they don't realize it's an option.</p>

<p><strong>Why this scope at this tier:</strong></p>
<ul>
  <li>Advanced internal marketing teams are usually senior and capable, but specialized depth in dashboard architecture, attribution infrastructure, or custom tooling is rare even at large companies. These are the gaps where external help compounds.</li>
  <li>Project-shaped engagements respect the reality that Advanced teams have strategic ownership. The partner builds capability, hands it over, and supports it, not "runs the program."</li>
  <li>The three services share a common thread: they're all about making the operational infrastructure more sophisticated, not about acquisition or branding which the internal team owns.</li>
</ul>

<h4>In-house vs. partner: the honest contrast</h4>
<p><strong>In-house works if you have:</strong> A marketing operations function with dedicated engineering, data, and analytics resources, plus the senior strategic leadership to direct them. At Advanced, in-house is the default. Most businesses at this tier run marketing as a real operational function, not as a series of vendor engagements.</p>

<p><strong>Partner works if you have:</strong> Specific capability gaps that internal hiring can't close fast enough, or one-off builds that don't justify dedicated headcount (a dashboard rebuild, an attribution overhaul, a custom marketing tool). The most common Advanced engagement at HMM is "internal team owns the program; we deliver specialized infrastructure projects on cycle." Six-month rolling project pipelines are typical. The partnership is collaborative, not delegative: the internal team brings the strategic context; we bring the specialized build capacity.</p>

<h4>What the audit doesn't address well at this tier</h4>
<p>At Advanced, the most consequential gaps aren't operational. They're strategic. Three frontiers the audit doesn't fully diagnose:</p>

<p><strong>1. Category position and brand pull.</strong> The primary recommendation above (12-month brand investment plan) is the right strategic move, but it's not an audit-shaped problem and it's not a HMM service. Hire a brand strategist or a category-design consultant for this work. Different discipline, different talent pool.</p>

<p><strong>2. Retention and lifecycle infrastructure.</strong> Same admission as Growing and Scaling: HMM doesn't currently offer dedicated lifecycle services. At Advanced, this is the most acute gap in our service map: your unit economics depend on it, your CAC is climbing, and the right answer is genuinely specialized expertise we don't have today. Partner with a retention-specialized agency or build the function internally with senior lifecycle marketers (not generalists doing email). This is the frontier where Advanced businesses compound past competitors.</p>

<p><strong>3. AI and automation infrastructure.</strong> Marketing AI tooling is changing faster than any agency can stay current. The Advanced businesses winning here have internal AI capability, not vendor relationships. HMM can build specific custom apps (Custom Apps service) but we're not your AI strategy partner. That's an internal capability or a specialized firm.</p>
      `.trim(),

      internalLinks: [
        { text: 'Read: How to think about marketing strategy', href: '/blog/marketing-strategy-from-zero' },
        { text: 'Explore: Analytics services', href: '/analytics' },
        { text: 'Discuss a custom dashboard or marketing tool build', href: '/contact' }
      ]
    }

  }
};

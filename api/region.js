// Consent region check, called by /consent.js on a visitor's first page view.
// Answers one question: does this visitor need to be asked before analytics run?
//
// Restricted (opt-in, banner shown): Quebec, the EU and EEA, the UK and its
// Crown Dependencies and Gibraltar, and Switzerland. Everyone else is open
// (analytics on by default, with the Privacy choices link to opt out).
//
// Vercel sets x-vercel-ip-country (ISO country) and x-vercel-ip-country-region
// (ISO 3166-2 subdivision, for example QC) at the edge and overwrites any value
// a client sends, so they cannot be spoofed from the browser. If either header
// is missing the answer is "restricted": the page fails closed to the banner.
//
// The response is per visitor, so it is never cached. Only the boolean is
// returned; the country and region stay on the server.
// Dependency-free, no package.json, matching the rest of /api.

// EU member states, then EEA (IS, LI, NO), UK (GB), Crown Dependencies and
// Gibraltar, Switzerland, and the EU's outermost-region and overseas codes that
// carry their own ISO country code.
var RESTRICTED_COUNTRIES = {};
(
  'AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE ' +
  'IS LI NO GB IM JE GG GI CH ' +
  'GP MQ GF RE YT BL MF PM'
).split(' ').forEach(function (c) { RESTRICTED_COUNTRIES[c] = true; });

// Province or territory codes inside otherwise open countries.
var RESTRICTED_REGIONS = { CA: { QC: true } };

function header(req, name) {
  var v = req.headers && req.headers[name];
  if (Array.isArray(v)) v = v[0];
  return typeof v === 'string' ? v.trim().toUpperCase() : '';
}

function isRestricted(country, region) {
  if (!country) return true;                     // unknown: fail closed
  if (RESTRICTED_COUNTRIES[country]) return true;
  var regions = RESTRICTED_REGIONS[country];
  if (regions) {
    if (!region) return true;                    // country needs a region and has none: fail closed
    return !!regions[region];
  }
  return false;
}

module.exports = function (req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('X-Robots-Tag', 'noindex');

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.statusCode = 405;
    return res.end(JSON.stringify({ error: 'method_not_allowed' }));
  }

  var restricted = isRestricted(header(req, 'x-vercel-ip-country'), header(req, 'x-vercel-ip-country-region'));
  res.statusCode = 200;
  res.end(JSON.stringify({ restricted: restricted }));
};


// Serves HTTP 410 Gone for retired WordPress URLs.
// Wired up via the /api/gone rewrites in vercel.json (Group B: /team/*,
// /category/*, /2025/* date archives, and any */feed). These pages are
// permanently removed, so 410 (not 404) tells Google to drop them for good.
module.exports = (req, res) => {
  res.statusCode = 410;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('X-Robots-Tag', 'noindex');
  res.end(
    '<!doctype html><meta charset="utf-8"><title>410 Gone</title>' +
    '<h1>410 Gone</h1><p>This page has been permanently removed.</p>'
  );
};

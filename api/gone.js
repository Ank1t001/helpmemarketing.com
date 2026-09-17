// Serves HTTP 410 Gone for retired WordPress-era URLs. Wired up by the
// /api/gone rewrites in vercel.json: /team/*, /category/*, /2025/*, /feed and
// any */feed, /wp-includes, /wp-content, /wp-admin (and their subpaths), and
// /xmlrpc.php. 410 rather than 404 tells search engines to drop them for good.
module.exports = (req, res) => {
  res.statusCode = 410;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('X-Robots-Tag', 'noindex');
  res.end(
    '<!doctype html><meta charset="utf-8"><title>410 Gone</title>' +
    '<h1>410 Gone</h1><p>This page has been permanently removed.</p>'
  );
};

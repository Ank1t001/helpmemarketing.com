"""Compute identities for an updated cycle; never approve editorial checks."""
import hashlib, json
from build_v2 import BASE, fingerprint, metrics
config=json.loads((BASE/'ig_cycle.json').read_text())
(BASE/'body_review.json').write_text(json.dumps({
    'cycle':config['cycle'], 'dataset_sha256':fingerprint(),
    'body_sha256':hashlib.sha256((BASE/'report_body.html').read_bytes()).hexdigest(),
    'publication_review':'pending',
    'note':'Verify all claims, frames, advertising and raw inputs before marking complete.'},indent=2))
(BASE/'cycle_metrics.json').write_text(json.dumps(metrics(),indent=2))
print('Updated file identities and metrics. Editorial approval remains pending.')

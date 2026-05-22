export function getScoreClass(score) {
  if (score >= 75) return 'score-high';
  if (score >= 50) return 'score-mid';
  return 'score-low';
}

export function getRecClass(rec) {
  const r = (rec || '').toLowerCase();
  if (r.includes('strong')) return 'rec-strong-hire';
  if (r.includes('hire') && !r.includes('no')) return 'rec-hire';
  if (r.includes('maybe')) return 'rec-maybe';
  return 'rec-no-hire';
}

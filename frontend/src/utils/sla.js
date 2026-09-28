export const SLA_DURATIONS_MS = Object.freeze({
  CRITICAL: 48 * 60 * 60 * 1000,
  MODERATE: 7 * 24 * 60 * 60 * 1000,
  MINOR: 30 * 24 * 60 * 60 * 1000,
});

export function calculateSlaState(createdAt, severityLevel, status, now = Date.now()) {
  if (status === 'ESCALATED') return { state: 'escalated', remainingMs: 0, progress: 0 };
  if (status === 'RESOLVED' || status === 'CANCELLED') {
    return { state: 'complete', remainingMs: 0, progress: 0 };
  }
  const duration = SLA_DURATIONS_MS[String(severityLevel || '').toUpperCase()];
  const created = Date.parse(createdAt);
  if (!duration || !Number.isFinite(created)) {
    return { state: 'pending', remainingMs: null, progress: null };
  }

  const elapsed = Math.max(0, now - created);
  const remainingMs = Math.max(0, duration - elapsed);
  const progress = Math.max(0, Math.min(1, remainingMs / duration));
  if (remainingMs === 0) return { state: 'overdue', remainingMs, progress };
  if (progress < 0.25) return { state: 'urgent', remainingMs, progress };
  if (progress <= 0.5) return { state: 'warning', remainingMs, progress };
  return { state: 'on-track', remainingMs, progress };
}

export function formatSlaDuration(milliseconds) {
  if (!Number.isFinite(milliseconds) || milliseconds <= 0) return '00:00:00';
  const totalSeconds = Math.floor(milliseconds / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const clock = [hours, minutes, seconds].map((value) => String(value).padStart(2, '0')).join(':');
  return days > 0 ? `${days}d ${clock}` : clock;
}

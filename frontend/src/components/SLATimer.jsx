import { useEffect, useState } from 'react';
import { calculateSlaState, formatSlaDuration } from '../utils/sla';

const STATE_STYLES = {
  'on-track': 'border-green-500/30 bg-green-500/10 text-green-300',
  warning: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-200',
  urgent: 'animate-pulse border-amber-500/40 bg-amber-500/10 text-amber-200',
  overdue: 'animate-pulse border-red-500/40 bg-red-500/10 text-red-300',
  escalated: 'animate-pulse border-red-500/40 bg-red-500/10 text-red-300',
  pending: 'border-gray-700 bg-gray-800 text-gray-400',
  complete: 'border-gray-700 bg-gray-800 text-gray-400',
};

export default function SLATimer({ createdAt, severityLevel, status }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  const sla = calculateSlaState(createdAt, severityLevel, status, now);
  let label;
  if (sla.state === 'escalated' || sla.state === 'overdue') label = 'SLA breached';
  else if (sla.state === 'pending') label = severityLevel === 'PENDING' ? 'Awaiting AI triage' : 'SLA unavailable';
  else if (sla.state === 'complete') label = status === 'RESOLVED' ? 'Resolved' : 'Cancelled';
  else label = `${formatSlaDuration(sla.remainingMs)} left`;

  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[11px] font-semibold ${STATE_STYLES[sla.state]}`}
      role="timer"
      aria-label={`Service deadline: ${label}`}
      title={createdAt ? `Created ${new Date(createdAt).toLocaleString()}` : undefined}
    >
      {label}
    </span>
  );
}

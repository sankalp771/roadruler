import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart3, Award } from 'lucide-react';

export default function PublicPortal() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    axios.get('/api/v1/public/stats')
      .then(({ data }) => { if (active) setStats(data); })
      .catch(() => { if (active) setError('Public statistics are temporarily unavailable. Please try again later.'); });
    return () => { active = false; };
  }, []);

  const number = (value) => new Intl.NumberFormat().format(value);
  const metric = (value, suffix = '') => stats ? `${number(value)}${suffix}` : '—';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2 text-center sm:text-left">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>City-Wide Open Data</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Public Transparency Portal
        </h1>
        <p className="text-sm text-gray-400 max-w-2xl">
          Publicly available complaint totals and resolution statistics, updated from reported municipal work.
        </p>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-blue-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Total Hazards Logged</span>
          <div className="text-3xl font-black text-white mt-1">{metric(stats?.total_complaints)}</div>
          <p className="text-xs text-gray-400 mt-2">Reports in the system</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-emerald-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Resolution Success Rate</span>
          <div className="text-3xl font-black text-emerald-400 mt-1">{metric(stats?.resolution_rate, '%')}</div>
          <p className="text-xs text-gray-400 mt-2">{metric(stats?.resolved_complaints)} reports resolved</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-purple-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Avg SLA Turnaround</span>
          <div className="text-3xl font-black text-purple-400 mt-1">{stats?.average_resolution_days == null ? '—' : `${number(stats.average_resolution_days)} Days`}</div>
          <p className="text-xs text-gray-400 mt-2">Average time for resolved reports</p>
        </div>
      </div>

      {error && <p role="status" className="text-sm text-amber-300">{error}</p>}

      {/* Leaderboard Scaffolding */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-400" />
              <span>Ward Performance Leaderboard</span>
            </h3>
            <p className="text-xs text-gray-400">Resolved share and average time for resolved reports</p>
          </div>
          <span className="text-xs text-blue-400 font-mono">{stats ? `Updated ${new Date(stats.generated_at).toLocaleString()}` : 'Loading'}</span>
        </div>

        {!error && stats?.wards.length === 0 && <p className="text-sm text-gray-400">Ward-level statistics will appear when reports have ward assignments.</p>}
        <div className="space-y-3 text-xs">
          {stats?.wards.map((ward, index) => (
            <div key={`${ward.ward_id}-${ward.department_name ?? ''}`} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className={`w-6 h-6 rounded-full font-bold flex items-center justify-center text-xs ${index === 0 ? 'bg-amber-500/20 text-amber-400' : 'bg-gray-700 text-gray-300'}`}>{index + 1}</span>
                <div>
                  <span className="font-bold text-white">{ward.department_name || `Ward ${ward.ward_id}`}</span>
                  <p className="text-[11px] text-gray-400">{number(ward.resolved_complaints)} of {number(ward.total_complaints)} resolved · {ward.average_resolution_days == null ? 'No resolution-time data' : `${number(ward.average_resolution_days)} days average`}</p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 font-bold">{number(ward.resolution_rate)}%</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}

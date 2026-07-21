import React from 'react';
import { BarChart3, TrendingUp, CheckCircle2, ShieldCheck, Award, Map } from 'lucide-react';

export default function PublicPortal() {
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
          Real-time open infrastructure analytics. Track municipal ward performance, resolution statistics, and verified repairs.
        </p>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-blue-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Total Hazards Logged</span>
          <div className="text-3xl font-black text-white mt-1">1,482</div>
          <p className="text-xs text-gray-400 mt-2">Verified citizen reports</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-emerald-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Resolution Success Rate</span>
          <div className="text-3xl font-black text-emerald-400 mt-1">89.4%</div>
          <p className="text-xs text-gray-400 mt-2">1,325 fixed within SLA</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border-l-4 border-l-purple-500">
          <span className="text-xs font-bold text-gray-400 uppercase">Avg SLA Turnaround</span>
          <div className="text-3xl font-black text-purple-400 mt-1">2.4 Days</div>
          <p className="text-xs text-gray-400 mt-2">Across 24 municipal wards</p>
        </div>
      </div>

      {/* Leaderboard Scaffolding */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-400" />
              <span>Ward Performance Leaderboard</span>
            </h3>
            <p className="text-xs text-gray-400">Ranked by resolution speed & citizen satisfaction</p>
          </div>
          <span className="text-xs text-blue-400 font-mono">Updated Live</span>
        </div>

        <div className="space-y-3 text-xs">
          <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center text-xs">1</span>
              <div>
                <span className="font-bold text-white">Ward 3 (K-West / Andheri West)</span>
                <p className="text-[11px] text-gray-400">96.8% resolution rate | Avg 1.2 days</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 font-bold">Top Performing</span>
          </div>

          <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-gray-700 text-gray-300 font-bold flex items-center justify-center text-xs">2</span>
              <div>
                <span className="font-bold text-white">Ward 5 (R-Central / Borivali)</span>
                <p className="text-[11px] text-gray-400">92.1% resolution rate | Avg 1.9 days</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 font-bold">High Speed</span>
          </div>
        </div>
      </div>

    </div>
  );
}

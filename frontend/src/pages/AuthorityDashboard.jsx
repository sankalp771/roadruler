import React from 'react';
import { Shield, AlertTriangle, Clock, CheckCircle2, Filter, Layers, ChevronRight } from 'lucide-react';

export default function AuthorityDashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Shield className="w-3.5 h-3.5" />
            <span>Municipal Authority Console</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight mt-1">
            Ward Officer Work Queue
          </h1>
          <p className="text-xs text-gray-400">
            Real-time hazard triage, priority severity ranking, and contractor work order dispatch.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button className="px-4 py-2 rounded-xl bg-gray-800 border border-gray-700 text-xs text-gray-200 hover:text-white font-medium flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <span>Filter Queue</span>
          </button>
          <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors shadow-md">
            + Dispatch Contractor
          </button>
        </div>
      </div>

      {/* Metrics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase">Active Complaints</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mt-2">142</div>
          <div className="text-[11px] text-blue-400 mt-1">18 new today</div>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase">Critical Hazards</span>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 text-red-400 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-red-400 mt-2">29</div>
          <div className="text-[11px] text-red-400 mt-1">&lt; 24h SLA remaining</div>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase">Avg Response Time</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">1.8 Days</div>
          <div className="text-[11px] text-emerald-400 mt-1">↓ 14% improvement</div>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase">Resolved This Week</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">87</div>
          <div className="text-[11px] text-gray-400 mt-1">94% citizen satisfaction</div>
        </div>

      </div>

      {/* Queue Table Scaffolding */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Priority Queue (Scheduled for Day 10 Table Implementation)
          </h3>
          <span className="text-xs text-gray-400">Showing 3 of 142 tickets</span>
        </div>

        <div className="divide-y divide-gray-800/80 text-xs">
          
          <div className="p-4 flex items-center justify-between hover:bg-gray-800/40 transition-colors">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 rounded bg-red-500/10 text-red-400 font-bold border border-red-500/20 text-[10px]">
                CRITICAL
              </span>
              <div>
                <p className="font-bold text-white">#RR-2026-89421 — Major Pothole Hazard</p>
                <p className="text-gray-400">SV Road, Ward 3 | Submitted 2h ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-amber-400 font-mono">SLA: 46h left</span>
              <ChevronRight className="w-4 h-4 text-gray-500" />
            </div>
          </div>

          <div className="p-4 flex items-center justify-between hover:bg-gray-800/40 transition-colors">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20 text-[10px]">
                MODERATE
              </span>
              <div>
                <p className="font-bold text-white">#RR-2026-89419 — Waterlogging & Drainage Block</p>
                <p className="text-gray-400">Link Road, Ward 2 | Submitted 5h ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-emerald-400 font-mono">SLA: 6d left</span>
              <ChevronRight className="w-4 h-4 text-gray-500" />
            </div>
          </div>

          <div className="p-4 flex items-center justify-between hover:bg-gray-800/40 transition-colors">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 text-[10px]">
                MINOR
              </span>
              <div>
                <p className="font-bold text-white">#RR-2026-89402 — Broken Streetlight Pole</p>
                <p className="text-gray-400">Western Express Hwy, Ward 5 | Submitted 1d ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-emerald-400 font-mono">SLA: 12d left</span>
              <ChevronRight className="w-4 h-4 text-gray-500" />
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}

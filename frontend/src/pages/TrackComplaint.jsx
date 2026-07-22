import React, { useState } from 'react';
import { Search, MapPin, CheckCircle2, Clock, ShieldAlert, Cpu } from 'lucide-react';

export default function TrackComplaint() {
  const [complaintId, setComplaintId] = useState('');

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <Search className="w-3.5 h-3.5" />
          <span>Real-Time Lookup</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Track Complaint Status
        </h1>
        <p className="text-sm text-gray-400">
          Enter your unique complaint tracking ID to view live repair progress, AI severity classification, and municipal SLA timelines.
        </p>
      </div>

      {/* Search Input Card */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <label className="text-xs font-bold text-gray-200 uppercase tracking-wider block">
          Lookup Complaint Ticket
        </label>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="e.g. RR-2026-89421"
              value={complaintId}
              onChange={(e) => setComplaintId(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-gray-500 font-mono"
            />
          </div>
          <button className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 shadow-md">
            <Search className="w-4 h-4" />
            <span>Search Ticket</span>
          </button>
        </div>
      </div>

      {/* Demo Status Timeline Preview */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div>
            <span className="text-xs text-gray-400 uppercase font-mono">Sample Ticket #RR-2026-89421</span>
            <h3 className="text-lg font-bold text-white">Severe Pothole — SV Road, Malad West</h3>
          </div>
          <span className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-bold flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>CRITICAL SEVERITY</span>
          </span>
        </div>

        {/* Timeline Steps */}
        <div className="space-y-4 pt-2">
          <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Resolution Lifecycle Timeline
          </h4>

          <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-800">
            
            {/* Step 1 */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-gray-900 flex items-center justify-center">
                <CheckCircle2 className="w-3 h-3 text-white" />
              </span>
              <div>
                <p className="text-sm font-bold text-white">1. Citizen Report Submitted</p>
                <p className="text-xs text-gray-400">Received with GPS tag: 19.1864° N, 72.8485° E</p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-gray-900 flex items-center justify-center">
                <Cpu className="w-3 h-3 text-white" />
              </span>
              <div>
                <p className="text-sm font-bold text-white">2. AI Vision Inference Completed</p>
                <p className="text-xs text-gray-400">YOLOv8 detected Pothole (Area ratio: 18.4%, Severity Score: 88/100)</p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-amber-500 ring-4 ring-gray-900 flex items-center justify-center">
                <Clock className="w-3 h-3 text-white animate-pulse" />
              </span>
              <div>
                <p className="text-sm font-bold text-amber-400">3. Assigned to PWD Ward 3 (In Progress)</p>
                <p className="text-xs text-gray-400">SLA Deadline: 48 Hours | Officer Assigned: A. Sharma</p>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}

import React from 'react';
import { AlertTriangle, MapPin, Camera, FileText, Send, Sparkles } from 'lucide-react';

export default function ReportIssue() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Citizen Issue Reporting</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Report a Road Hazard
        </h1>
        <p className="text-sm text-gray-400">
          Upload geo-tagged evidence and pin the exact location. Our AI engine will detect hazard severity and route to authorities.
        </p>
      </div>

      {/* Form Scaffolding Container */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        
        {/* Step Indicator */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 pb-6 border-b border-gray-800 text-center">
          <div className="space-y-1">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold">1</span>
            <p className="text-xs font-medium text-blue-400">Photo Evidence</p>
          </div>
          <div className="space-y-1 opacity-70">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-800 text-gray-400 text-xs font-bold">2</span>
            <p className="text-xs font-medium text-gray-400">Hazard Details</p>
          </div>
          <div className="space-y-1 opacity-70">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-800 text-gray-400 text-xs font-bold">3</span>
            <p className="text-xs font-medium text-gray-400">Map Pin Location</p>
          </div>
        </div>

        {/* Photo Upload Zone Placeholder */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
            <Camera className="w-4 h-4 text-blue-400" />
            <span>Hazard Evidence Photo</span>
          </label>
          <div className="border-2 border-dashed border-gray-700/80 hover:border-blue-500/50 rounded-xl p-8 text-center bg-gray-900/40 transition-colors cursor-pointer group">
            <Camera className="w-10 h-10 mx-auto text-gray-500 group-hover:text-blue-400 transition-colors mb-3" />
            <p className="text-xs font-medium text-gray-300">
              Drag & drop photo here or <span className="text-blue-400 hover:underline">browse files</span>
            </p>
            <p className="text-[11px] text-gray-500 mt-1">PNG, JPG, WEBP up to 10MB (GPS tags automatically extracted)</p>
          </div>
        </div>

        {/* Hazard Category Dropdown Scaffolding */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-400" />
            <span>Hazard Category</span>
          </label>
          <select className="w-full px-4 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-gray-200 text-sm focus:outline-none focus:border-blue-500">
            <option value="POTHOLE">Pothole (Severe Surface Cavity)</option>
            <option value="WATERLOGGING">Waterlogging & Flooding</option>
            <option value="BROKEN_STREETLIGHT">Broken Streetlight / Dark Spot</option>
            <option value="DAMAGED_SURFACE">Damaged Surface / Alligator Cracks</option>
            <option value="TRAFFIC_HAZARD">Obstruction / Traffic Safety Hazard</option>
          </select>
        </div>

        {/* Map Location Scaffolding */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
            <MapPin className="w-4 h-4 text-blue-400" />
            <span>Location Pin Picker</span>
          </label>
          <div className="h-64 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-center text-center p-4">
            <div className="space-y-2">
              <MapPin className="w-8 h-8 text-blue-500 animate-bounce mx-auto" />
              <p className="text-xs text-gray-400">
                Leaflet OpenStreetMap Location Picker (Scheduled for Day 3 Integration)
              </p>
              <p className="text-[11px] text-gray-500 font-mono">
                Default Coordinates: 19.0760° N, 72.8777° E (Mumbai)
              </p>
            </div>
          </div>
        </div>

        {/* Submit Action */}
        <button
          disabled
          className="w-full py-3.5 rounded-xl bg-blue-600/50 text-white/70 font-semibold text-sm flex items-center justify-center gap-2 cursor-not-allowed border border-blue-500/20"
        >
          <Send className="w-4 h-4" />
          <span>Submit Report (Day 4 Feature)</span>
        </button>

      </div>
    </div>
  );
}

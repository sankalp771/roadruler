import React from 'react';
import { MapPin, Shield, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-gray-950 border-t border-gray-800/80 text-gray-400 py-12 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Col 1: System Info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <MapPin className="w-4 h-4" />
              </div>
              <span className="font-bold text-lg text-white">
                Road<span className="text-blue-500">Ruler</span>
              </span>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              AI-driven civic infrastructure management platform leveraging computer vision hazard detection, spatial proximity deduplication, and automated municipal SLA routing.
            </p>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider mb-3">
              Platform Views
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/" className="hover:text-blue-400 transition-colors">Home & Overview</Link>
              </li>
              <li>
                <Link to="/report" className="hover:text-blue-400 transition-colors">Report Road Hazard</Link>
              </li>
              <li>
                <Link to="/track" className="hover:text-blue-400 transition-colors">Complaint Tracker</Link>
              </li>
              <li>
                <Link to="/authority" className="hover:text-blue-400 transition-colors">Authority Dashboard</Link>
              </li>
              <li>
                <Link to="/public" className="hover:text-blue-400 transition-colors">Public Analytics Portal</Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Technical Stack */}
          <div>
            <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider mb-3">
              Technical Stack
            </h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                <span>Vite + React 19 & TailwindCSS</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                <span>FastAPI & Neon PostgreSQL (PostGIS)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                <span>YOLOv8 Hazard Vision & ResNet50</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                <span>Leaflet.js & OpenStreetMap</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Development Team */}
          <div>
            <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider mb-3">
              Engineering Team
            </h4>
            <div className="space-y-2 text-xs">
              <p className="flex justify-between items-center py-1 border-b border-gray-800/60">
                <span className="text-gray-300 font-medium">Milin Kanu</span>
                <span className="text-[10px] text-blue-400 px-1.5 py-0.5 rounded bg-blue-500/10">Frontend & UI</span>
              </p>
              <p className="flex justify-between items-center py-1 border-b border-gray-800/60">
                <span className="text-gray-300 font-medium">Utkarsh Mishra</span>
                <span className="text-[10px] text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-500/10">Backend & API</span>
              </p>
              <p className="flex justify-between items-center py-1">
                <span className="text-gray-300 font-medium">Sankalp Pandey</span>
                <span className="text-[10px] text-amber-400 px-1.5 py-0.5 rounded bg-amber-500/10">AI & Vision</span>
              </p>
            </div>
          </div>

        </div>

        <div className="pt-6 border-t border-gray-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <p>© {new Date().getFullYear()} RoadRuler Civic Tech Ecosystem. All rights reserved.</p>
          <div className="flex items-center gap-1 text-gray-500">
            <span>Built with</span>
            <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500" />
            <span>at Thakur College of Engineering & Technology</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

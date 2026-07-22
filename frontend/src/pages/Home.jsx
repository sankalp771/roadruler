import React from 'react';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  MapPin, 
  Search, 
  Shield, 
  Sparkles, 
  Zap, 
  Layers, 
  CheckCircle2, 
  Clock, 
  ArrowRight,
  TrendingUp,
  Activity,
  Cpu
} from 'lucide-react';

export default function Home() {
  return (
    <div className="space-y-16 pb-16">
      
      {/* Hero Section */}
      <section className="relative pt-12 pb-8 overflow-hidden">
        {/* Background Ambient Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute top-1/3 left-1/4 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide mb-6 glow-blue">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>AI-Enhanced Civic Infrastructure Ecosystem</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">
            Report Road Hazards. <br />
            <span className="gradient-text">Power Proactive Municipal Repairs.</span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed font-normal">
            Transforming reactive citizen complaints into automated municipal action using <span className="text-white font-medium">YOLOv8 Hazard Detection</span>, <span className="text-white font-medium">ResNet50 Deduplication</span>, and <span className="text-white font-medium">PostGIS Geo-Spatial Routing</span>.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/report"
              className="flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold text-sm shadow-lg shadow-blue-500/25 transition-all duration-200 active:scale-95 w-full sm:w-auto"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Report Road Issue</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/track"
              className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-gray-800/80 hover:bg-gray-800 border border-gray-700/80 text-gray-200 hover:text-white font-semibold text-sm transition-all duration-200 w-full sm:w-auto"
            >
              <Search className="w-4 h-4 text-gray-400" />
              <span>Track Complaint Status</span>
            </Link>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="glass-card p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-white">99.2%</div>
              <div className="text-xs text-gray-400 font-medium mt-0.5">AI Detection Accuracy</div>
            </div>
            <div className="glass-card p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-emerald-400">&lt; 15m</div>
              <div className="text-xs text-gray-400 font-medium mt-0.5">Proximity Deduplication</div>
            </div>
            <div className="glass-card p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-blue-400">48h SLA</div>
              <div className="text-xs text-gray-400 font-medium mt-0.5">Critical Ticket Escalation</div>
            </div>
            <div className="glass-card p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-amber-400">100%</div>
              <div className="text-xs text-gray-400 font-medium mt-0.5">Open Source Tech</div>
            </div>
          </div>

        </div>
      </section>

      {/* Feature Cards Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            End-to-End Civic Infrastructure Intelligence
          </h2>
          <p className="text-sm text-gray-400 mt-2">
            Engineered with modern web technologies and deep learning AI pipelines.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Computer Vision Detection</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Upload geo-tagged evidence. Our deep-learning YOLOv8 inference worker analyzes pothole dimensions, severe cracks, and waterlogging to generate instant severity scores.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-110 transition-transform">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Spatial Proximity Deduplication</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Prevents spam duplicate tickets within 50 meters using PostGIS spatial indexing combined with ResNet50 cosine image feature similarity merging.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4 group-hover:scale-110 transition-transform">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Authority Routing & SLA Engine</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Automated spatial polygon intersection routes tickets directly to responsible municipal ward officers, enforcing live SLA resolution timers.
            </p>
          </div>

        </div>
      </section>

      {/* Role Navigation Quick Links */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel p-8 rounded-3xl border border-gray-800 relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Navigation Shortcuts</span>
              <h3 className="text-2xl font-bold text-white">Explore RoadRuler Portal Modules</h3>
              <p className="text-xs text-gray-400 max-w-xl">
                Access citizen reporting tools, municipal officer work queues, or public transparency metrics.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/authority" className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-medium text-xs border border-gray-700 transition-colors flex items-center gap-2">
                <Shield className="w-4 h-4 text-blue-400" />
                <span>Authority Portal</span>
              </Link>
              <Link to="/public" className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-medium text-xs border border-gray-700 transition-colors flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Public Analytics</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}

import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { 
  MapPin, 
  AlertTriangle, 
  Search, 
  Shield, 
  BarChart3, 
  PlusCircle, 
  Menu, 
  X,
  Sparkles
} from 'lucide-react';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Home', icon: MapPin },
    { path: '/report', label: 'Report Hazard', icon: AlertTriangle },
    { path: '/track', label: 'Track Issue', icon: Search },
    { path: '/authority', label: 'Authority Portal', icon: Shield },
    { path: '/public', label: 'Public Transparency', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-gray-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400 group-hover:bg-blue-600/30 group-hover:border-blue-500/50 transition-all duration-300 glow-blue">
              <MapPin className="w-5 h-5 text-blue-400 animate-pulse" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-blue-400 transition-colors">
                  Road<span className="text-blue-500">Ruler</span>
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-gray-400 font-medium hidden sm:block">
                AI Infrastructure Management
              </p>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                        : 'text-gray-300 hover:text-white hover:bg-gray-800/60 border border-transparent'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Desktop Right Action Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/report"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-medium text-xs shadow-md shadow-blue-500/20 hover:shadow-blue-500/35 transition-all duration-200 active:scale-95"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Report Issue</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/80 focus:outline-none"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-b border-gray-800 px-4 pt-2 pb-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                      : 'text-gray-300 hover:bg-gray-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          <div className="pt-2 border-t border-gray-800">
            <Link
              to="/report"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-md"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Report Hazard Now</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}

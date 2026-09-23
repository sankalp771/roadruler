import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import ReportIssue from './pages/ReportIssue';
import TrackComplaint from './pages/TrackComplaint';
import AuthorityDashboard from './pages/AuthorityDashboard';
import PublicPortal from './pages/PublicPortal';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-[#0B0F19] text-gray-100 selection:bg-blue-500/30 selection:text-blue-200">
        <Toaster 
          position="top-right" 
          toastOptions={{
            duration: 4000,
            style: {
              background: '#111827',
              color: '#F3F4F6',
              border: '1px solid #374151',
              borderRadius: '0.75rem',
            },
          }} 
        />
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route 
              path="/report" 
              element={
                <ProtectedRoute>
                  <ReportIssue />
                </ProtectedRoute>
              } 
            />
            <Route path="/track" element={<TrackComplaint />} />
            <Route path="/authority" element={<AuthorityDashboard />} />
            <Route path="/public" element={<PublicPortal />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}


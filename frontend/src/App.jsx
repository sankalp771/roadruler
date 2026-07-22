import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import ReportIssue from './pages/ReportIssue';
import TrackComplaint from './pages/TrackComplaint';
import AuthorityDashboard from './pages/AuthorityDashboard';
import PublicPortal from './pages/PublicPortal';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-[#0B0F19] text-gray-100 selection:bg-blue-500/30 selection:text-blue-200">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/report" element={<ReportIssue />} />
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

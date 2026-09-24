import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AuthorityDashboard from './AuthorityDashboard';

export default function AdminDashboard() {
  const { user, openSignInModal } = useAuth();

  if (user?.roleId !== 'ADMIN') {
    return (
      <section className="mx-auto my-16 max-w-lg rounded-2xl border border-gray-800 bg-gray-900/70 p-8 text-center">
        <ShieldAlert className="mx-auto h-9 w-9 text-purple-400" />
        <h1 className="mt-4 text-xl font-bold text-white">Admin access required</h1>
        <p className="mt-2 text-sm text-gray-400">Sign in with an Admin profile to open the system dashboard.</p>
        <button onClick={openSignInModal} className="mt-5 rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-500">Choose Admin profile</button>
      </section>
    );
  }

  return (
    <div>
      <header className="mx-auto mt-7 flex max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
        <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-3 text-purple-300"><Cpu className="h-6 w-6" /></div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-purple-300">System administration · {user.fullName}</p>
          <h1 className="text-2xl font-extrabold text-white">RoadRuler Admin Console</h1>
        </div>
        <Link to="/public" className="ml-auto text-sm text-blue-300 hover:text-blue-200">Public dashboard →</Link>
      </header>
      <AuthorityDashboard />
    </div>
  );
}

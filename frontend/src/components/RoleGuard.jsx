import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

function hasAllowedRole(user, allowedRoles) {
  if (!user) return false;
  const role = String(user.roleId || '').toUpperCase();
  // The local demo's AUTHORITY label represents a Clerk WARD_OFFICER role.
  const normalizedRole = user.isDemo && role === 'AUTHORITY' ? 'WARD_OFFICER' : role;
  return allowedRoles.map((allowedRole) => String(allowedRole).trim().toUpperCase()).includes(normalizedRole);
}

export default function RoleGuard({ children, allowedRoles }) {
  const { isLoaded, isSignedIn, user, openSignInModal } = useAuth();

  if (!isLoaded) return <div className="min-h-[40vh]" role="status">Checking access…</div>;
  if (!isSignedIn) {
    return (
      <section className="mx-auto my-16 max-w-lg rounded-2xl border border-gray-800 p-8 text-center glass-panel">
        <h1 className="text-xl font-bold text-white">Sign in required</h1>
        <p className="mt-2 text-sm text-gray-400">Sign in with an authorized municipal account to continue.</p>
        <button onClick={openSignInModal} className="mt-5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white">Sign in</button>
      </section>
    );
  }
  if (!hasAllowedRole(user, allowedRoles)) {
    return (
      <section className="mx-auto my-16 max-w-lg rounded-2xl border border-red-500/30 p-8 text-center glass-panel" role="alert">
        <ShieldAlert className="mx-auto h-10 w-10 text-red-400" />
        <p className="mt-3 text-xs font-bold uppercase tracking-widest text-red-300">403 · Access denied</p>
        <h1 className="mt-2 text-xl font-bold text-white">Authority access only</h1>
        <p className="mt-2 text-sm text-gray-400">Your account does not have permission to view this municipal dashboard.</p>
      </section>
    );
  }
  return children;
}

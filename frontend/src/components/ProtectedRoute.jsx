import React from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, LogIn, Loader2 } from 'lucide-react';

export default function ProtectedRoute({ children }) {
  const { isLoaded, isSignedIn, openSignInModal } = useAuth();

  if (!isLoaded) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-sm text-gray-400 font-medium">Verifying authentication session...</p>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 glass-panel rounded-2xl border border-gray-800 text-center space-y-6">
        <div className="w-14 h-14 mx-auto rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
          <ShieldAlert className="w-7 h-7 text-blue-400" />
        </div>
        
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white tracking-tight">Authentication Required</h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            You must be signed in to submit hazard reports or access restricted citizen features.
          </p>
        </div>

        <button
          onClick={openSignInModal}
          className="w-full py-3 px-6 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20 active:scale-95 cursor-pointer"
        >
          <LogIn className="w-4 h-4" />
          <span>Sign In to Continue</span>
        </button>
      </div>
    );
  }

  return children;
}

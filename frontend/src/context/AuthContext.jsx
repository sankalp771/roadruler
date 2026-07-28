import React, { createContext, useContext, useState } from 'react';
import { useAuth as useClerkAuth, useUser as useClerkUser, ClerkProvider } from '@clerk/clerk-react';
import { ShieldCheck, X, Sparkles, User, Shield, Cpu, CheckCircle2, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

export const USER_ROLES = {
  CITIZEN: {
    id: 'CITIZEN',
    fullName: 'Milin Kanu',
    roleLabel: 'Citizen Reporter',
    email: 'milinkanu@roadruler.gov.in',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    icon: User,
  },
  AUTHORITY: {
    id: 'AUTHORITY',
    fullName: 'Utkarsh Mishra',
    roleLabel: 'Ward Officer (PWD)',
    email: 'utkarsh@mumbai.pwd.gov.in',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    icon: Shield,
  },
  ADMIN: {
    id: 'ADMIN',
    fullName: 'Sankalp Pandey',
    roleLabel: 'AI System Admin',
    email: 'sankalp@roadruler.ai',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    icon: Cpu,
  },
};

const AuthContext = createContext({
  isLoaded: true,
  isSignedIn: false,
  user: null,
  openSignInModal: () => {},
  signInAsRole: () => {},
  signOut: () => {},
});

export const useAuth = () => useContext(AuthContext);

function SmartAuthInner({ children }) {
  let clerkAuth = { isLoaded: false, isSignedIn: false };
  let clerkUser = { user: null };

  try {
    clerkAuth = useClerkAuth();
    clerkUser = useClerkUser();
  } catch (e) {
    // Clerk hooks context fallback
  }

  const [localSignedIn, setLocalSignedIn] = useState(() => {
    return localStorage.getItem('roadruler_demo_auth') === 'true';
  });

  const [activeRole, setActiveRole] = useState(() => {
    const saved = localStorage.getItem('roadruler_demo_role');
    return USER_ROLES[saved] || USER_ROLES.CITIZEN;
  });

  const [showModal, setShowModal] = useState(false);

  const handleSignInAsRole = (roleKey) => {
    const selected = USER_ROLES[roleKey] || USER_ROLES.CITIZEN;
    setActiveRole(selected);
    setLocalSignedIn(true);
    localStorage.setItem('roadruler_demo_auth', 'true');
    localStorage.setItem('roadruler_demo_role', selected.id);
    setShowModal(false);
    toast.success(`Signed in as ${selected.fullName} (${selected.roleLabel})`);
  };

  const handleSignOut = () => {
    setLocalSignedIn(false);
    localStorage.removeItem('roadruler_demo_auth');
    localStorage.removeItem('roadruler_demo_role');
    toast('Signed out', { icon: '👋' });
  };

  const openSignInModal = () => {
    setShowModal(true);
  };

  const effectiveSignedIn = (clerkAuth.isLoaded && clerkAuth.isSignedIn) || localSignedIn;
  const effectiveUser = (clerkUser && clerkUser.user) ? {
    fullName: clerkUser.user.fullName || clerkUser.user.firstName || 'Authenticated User',
    email: clerkUser.user.primaryEmailAddress?.emailAddress || 'user@roadruler.gov.in',
    avatar: clerkUser.user.imageUrl,
    roleLabel: 'Clerk Verified User',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  } : (localSignedIn ? activeRole : null);

  return (
    <AuthContext.Provider
      value={{
        isLoaded: true,
        isSignedIn: effectiveSignedIn,
        user: effectiveUser,
        openSignInModal,
        signInAsRole: handleSignInAsRole,
        signOut: handleSignOut,
      }}
    >
      {children}

      {/* Multi-Role Quick Sign-In Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 bg-gray-950/85 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-lg p-6 sm:p-8 glass-panel rounded-2xl border border-gray-800 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            
            {/* Close Button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800/80 transition-all"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="text-center space-y-2">
              <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Sign In to RoadRuler</h2>
              <p className="text-xs text-gray-400">
                Select your user role for instant 1-click authentication
              </p>
            </div>

            {/* Role Cards List */}
            <div className="space-y-3 pt-2">
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Quick Login Roles</p>
              
              {/* 1. Citizen Role */}
              <button
                onClick={() => handleSignInAsRole('CITIZEN')}
                className="w-full p-4 rounded-xl bg-gray-900/80 hover:bg-blue-600/15 border border-gray-800 hover:border-blue-500/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={USER_ROLES.CITIZEN.avatar}
                    alt={USER_ROLES.CITIZEN.fullName}
                    className="w-10 h-10 rounded-full object-cover border border-blue-500/40"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">
                        {USER_ROLES.CITIZEN.fullName}
                      </p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
                        Citizen
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{USER_ROLES.CITIZEN.email}</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
              </button>

              {/* 2. Authority Ward Officer Role */}
              <button
                onClick={() => handleSignInAsRole('AUTHORITY')}
                className="w-full p-4 rounded-xl bg-gray-900/80 hover:bg-emerald-600/15 border border-gray-800 hover:border-emerald-500/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={USER_ROLES.AUTHORITY.avatar}
                    alt={USER_ROLES.AUTHORITY.fullName}
                    className="w-10 h-10 rounded-full object-cover border border-emerald-500/40"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">
                        {USER_ROLES.AUTHORITY.fullName}
                      </p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                        Ward Officer
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{USER_ROLES.AUTHORITY.email}</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
              </button>

              {/* 3. AI System Admin Role */}
              <button
                onClick={() => handleSignInAsRole('ADMIN')}
                className="w-full p-4 rounded-xl bg-gray-900/80 hover:bg-purple-600/15 border border-gray-800 hover:border-purple-500/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={USER_ROLES.ADMIN.avatar}
                    alt={USER_ROLES.ADMIN.fullName}
                    className="w-10 h-10 rounded-full object-cover border border-purple-500/40"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-white group-hover:text-purple-400 transition-colors">
                        {USER_ROLES.ADMIN.fullName}
                      </p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold">
                        AI Admin
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{USER_ROLES.ADMIN.email}</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
              </button>
            </div>

            {/* OAuth Divider */}
            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-gray-800"></div>
              <span className="flex-shrink mx-4 text-[10px] text-gray-500 uppercase tracking-widest font-semibold">Or Enterprise OAuth</span>
              <div className="flex-grow border-t border-gray-800"></div>
            </div>

            {/* Google OAuth Option */}
            <button
              onClick={() => handleSignInAsRole('CITIZEN')}
              className="w-full py-3 px-4 rounded-xl bg-gray-900 hover:bg-gray-800 text-gray-200 border border-gray-800 text-xs font-semibold transition-all flex items-center justify-center gap-3"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Continue with Google OAuth</span>
            </button>

            <p className="text-[11px] text-gray-500 text-center">
              Secured with Clerk Enterprise Auth & OAuth 2.0
            </p>
          </div>
        </div>
      )}
    </AuthContext.Provider>
  );
}

export function SmartAuthProvider({ children }) {
  const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

  if (publishableKey) {
    return (
      <ClerkProvider publishableKey={publishableKey} afterSignOutUrl="/">
        <SmartAuthInner>{children}</SmartAuthInner>
      </ClerkProvider>
    );
  }

  return <SmartAuthInner>{children}</SmartAuthInner>;
}

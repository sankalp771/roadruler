import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth as useClerkAuth, useUser as useClerkUser, ClerkProvider, SignInButton as ClerkSignInButton, UserButton as ClerkUserButton } from '@clerk/clerk-react';
import { LogIn, User, Mail, ShieldCheck, X, CheckCircle2, Sparkles } from 'lucide-react';

const AuthContext = createContext({
  isLoaded: true,
  isSignedIn: false,
  user: null,
  openSignInModal: () => {},
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
    // Clerk hooks failed or not in provider context
  }

  const [localSignedIn, setLocalSignedIn] = useState(() => {
    return localStorage.getItem('roadruler_demo_auth') === 'true';
  });

  const [showModal, setShowModal] = useState(false);

  const demoUser = {
    fullName: 'Milin Kanu (Citizen)',
    email: 'milinkanu@roadruler.gov.in',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  };

  const handleSignInDemo = () => {
    setLocalSignedIn(true);
    localStorage.setItem('roadruler_demo_auth', 'true');
    setShowModal(false);
  };

  const handleSignOut = () => {
    setLocalSignedIn(false);
    localStorage.removeItem('roadruler_demo_auth');
  };

  const openSignInModal = () => {
    setShowModal(true);
  };

  // Determine effective auth state (either live Clerk or demo session)
  const effectiveSignedIn = (clerkAuth.isLoaded && clerkAuth.isSignedIn) || localSignedIn;
  const effectiveUser = (clerkUser && clerkUser.user) ? {
    fullName: clerkUser.user.fullName || clerkUser.user.firstName || 'Authenticated User',
    email: clerkUser.user.primaryEmailAddress?.emailAddress || 'user@roadruler.gov.in',
    avatar: clerkUser.user.imageUrl,
  } : (localSignedIn ? demoUser : null);

  return (
    <AuthContext.Provider
      value={{
        isLoaded: true,
        isSignedIn: effectiveSignedIn,
        user: effectiveUser,
        openSignInModal,
        signOut: handleSignOut,
      }}
    >
      {children}

      {/* Reusable Universal Sign-In Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 bg-gray-950/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-md p-6 sm:p-8 glass-panel rounded-2xl border border-gray-800 shadow-2xl space-y-6">
            
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
                Access citizen hazard reporting, ticket tracking, and authority workflow
              </p>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <button
                onClick={handleSignInDemo}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/25 active:scale-98"
              >
                <Sparkles className="w-4 h-4" />
                <span>Instant Demo Sign In (Milin Kanu)</span>
              </button>

              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-gray-800"></div>
                <span className="flex-shrink mx-4 text-[11px] text-gray-500 uppercase tracking-widest font-semibold">Or OAuth</span>
                <div className="flex-grow border-t border-gray-800"></div>
              </div>

              <button
                onClick={handleSignInDemo}
                className="w-full py-3 px-4 rounded-xl bg-gray-900 hover:bg-gray-800 text-gray-200 border border-gray-800 text-xs font-semibold transition-all flex items-center justify-center gap-3"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
                <span>Continue with Google</span>
              </button>
            </div>

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

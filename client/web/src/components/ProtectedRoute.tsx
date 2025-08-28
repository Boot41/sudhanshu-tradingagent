import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, token } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [hasValidAuth, setHasValidAuth] = useState(false);

  useEffect(() => {
    // Check authentication state
    const checkAuth = () => {
      const storedToken = localStorage.getItem('access_token');
      const authValid = isAuthenticated && !!(token || storedToken);
      
      setHasValidAuth(authValid);
      setIsLoading(false);
    };

    // Small delay to allow Zustand to rehydrate from persistence
    const timer = setTimeout(checkAuth, 150);
    return () => clearTimeout(timer);
  }, [isAuthenticated, token]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!hasValidAuth) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

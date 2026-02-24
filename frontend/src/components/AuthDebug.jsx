import { useAuth } from '../context/AuthContext';

export default function AuthDebug() {
  const { user, isAuthenticated, loading } = useAuth();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs font-mono z-50">
      <div className="font-bold mb-2">🔍 Auth Debug</div>
      <div>Loading: {loading ? 'true' : 'false'}</div>
      <div>Authenticated: {isAuthenticated ? 'true' : 'false'}</div>
      <div>User: {user ? user.email : 'null'}</div>
      <div>Token: {localStorage.getItem('token') ? 'exists' : 'none'}</div>
    </div>
  );
}
import React, { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        navigate('/');
      } else {
        setError('Invalid username or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, var(--color-slate-900) 0%, var(--color-slate-800) 100%)',
      padding: 'var(--spacing-xl)',
    }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 700 }}>
            🚀 EVER Platform
          </h1>
          <p className="text-gray-500" style={{ margin: 0 }}>
            v5.0 Enterprise Scraper Dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="username" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
              Username
            </label>
            <input
              id="username"
              type="text"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              placeholder="Enter username"
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter password"
            />
          </div>

          {error && (
            <div style={{
              marginBottom: '1rem',
              padding: '0.75rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              borderRadius: '0.5rem',
              color: 'var(--color-error)',
              fontSize: '0.875rem',
            }}>
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginBottom: '1rem' }}
            disabled={isLoading}
          >
            {isLoading ? <LoadingSpinner message="" /> : 'Sign In'}
          </button>
        </form>

        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          background: 'var(--color-gray-50)',
          borderRadius: '0.5rem',
          fontSize: '0.875rem',
        }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600 }}>Demo Credentials:</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontFamily: 'var(--font-mono)' }}>
            <div>admin / admin123</div>
            <div>viewer / viewer123</div>
            <div>operator / operator123</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;


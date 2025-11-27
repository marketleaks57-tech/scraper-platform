import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/hub', label: 'Analytics Hub', icon: '🎯' },
    { path: '/runs', label: 'Run Inspector', icon: '🔍' },
    { path: '/flow', label: 'Execution Flow', icon: '⚡' },
    { path: '/sources', label: 'Source Health', icon: '🏥' },
    { path: '/costs', label: 'Cost Tracking', icon: '💰' },
    { path: '/audit', label: 'Audit Events', icon: '📋' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/airflow/manage', label: 'Airflow', icon: '🔄' },
    { path: '/deploy', label: 'Deploy Scraper', icon: '🚀' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">
          <span>🚀</span>
          <span>EVER Platform</span>
        </h1>
        <p className="sidebar-subtitle">v5.0 Enterprise Scraper</p>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
        {user && (
          <div style={{
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '0.5rem',
            marginBottom: '1rem',
          }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>
              {user.username}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-400)' }}>
              {user.email}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)', marginTop: '0.25rem' }}>
              Role: {user.role}
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="btn btn-secondary"
          style={{
            width: '100%',
            background: 'rgba(239, 68, 68, 0.1)',
            color: 'var(--color-error)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
          }}
        >
          Logout
        </button>
        <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--color-gray-500)', textAlign: 'center' }}>
          <p style={{ margin: 0 }}>© 2024 EVER Platform</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Dashboard from './pages/Dashboard';
import AirflowView from './pages/AirflowView';
import AirflowManagement from './pages/AirflowManagement';
import RunInspector from './pages/RunInspector';
import Login from './pages/Login';
import CostTracking from './pages/CostTracking';
import AuditEvents from './pages/AuditEvents';
import SourceHealth from './pages/SourceHealth';
import PerformanceAnalytics from './pages/PerformanceAnalytics';
import AnalyticsHub from './pages/AnalyticsHub';
import ExecutionFlow from './pages/ExecutionFlow';
import DeployScraper from './pages/DeployScraper';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="app-root">
                <Sidebar />
                <main className="main-content">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/hub" element={<AnalyticsHub />} />
                    <Route path="/runs" element={<RunInspector />} />
                    <Route path="/flow" element={<ExecutionFlow />} />
                    <Route path="/airflow" element={<AirflowView />} />
                    <Route path="/airflow/manage" element={<AirflowManagement />} />
                    <Route path="/costs" element={<CostTracking />} />
                    <Route path="/audit" element={<AuditEvents />} />
                    <Route path="/sources" element={<SourceHealth />} />
                    <Route path="/analytics" element={<PerformanceAnalytics />} />
                    <Route path="/deploy" element={<DeployScraper />} />
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
};

export default App;

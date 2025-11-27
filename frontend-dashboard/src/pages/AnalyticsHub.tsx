import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

interface RunSummary {
  id: string;
  source: string;
  status: string;
  startedAt: string;
  finishedAt?: string;
  durationSeconds?: number;
  variantId?: string;
}

interface LogEntry {
  timestamp: string;
  level: string;
  source: string;
  run_id?: string;
  message: string;
  metadata?: Record<string, unknown>;
}

interface ProcessStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  lastCheck: string;
  details: string;
}

const AnalyticsHub: React.FC = () => {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [processes, setProcesses] = useState<ProcessStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState<string>('all');
  const [logLevel, setLogLevel] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Load runs
  useEffect(() => {
    const loadRuns = async () => {
      try {
        const resp = await fetch('/api/runs?limit=100');
        if (resp.ok) {
          const data = await resp.json();
          setRuns(data);
        }
      } catch (err) {
        console.error('Failed to load runs', err);
      }
    };
    loadRuns();
    if (autoRefresh) {
      const interval = setInterval(loadRuns, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Load logs
  useEffect(() => {
    const loadLogs = async () => {
      try {
        // TODO: Replace with actual logs API
        const resp = await fetch('/api/logs?limit=100');
        if (resp.ok) {
          const data = await resp.json();
          setLogs(data.logs || []);
        } else {
          // Fallback to mock
          const mockLogs: LogEntry[] = [
            {
              timestamp: new Date().toISOString(),
              level: 'info',
              source: 'alfabeta',
              run_id: 'run_2024_001',
              message: 'Starting pipeline execution',
            },
            {
              timestamp: new Date(Date.now() - 60000).toISOString(),
              level: 'info',
              source: 'alfabeta',
              run_id: 'run_2024_001',
              message: 'Fetched 1200 product URLs',
            },
            {
              timestamp: new Date(Date.now() - 120000).toISOString(),
              level: 'warning',
              source: 'quebec',
              run_id: 'run_2024_002',
              message: 'Drift detected on listing page',
            },
          ];
          setLogs(mockLogs);
        }
      } catch (err) {
        console.error('Failed to load logs', err);
      }
    };
    loadLogs();
    if (autoRefresh) {
      const interval = setInterval(loadLogs, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Load process status
  useEffect(() => {
    const loadProcesses = async () => {
      try {
        const [healthResp, airflowResp] = await Promise.all([
          fetch('/api/health'),
          fetch('/api/airflow/runs?limit=1'),
        ]);

        const processes: ProcessStatus[] = [];

        if (healthResp.ok) {
          processes.push({
            name: 'API Server',
            status: 'healthy',
            lastCheck: new Date().toISOString(),
            details: 'API responding normally',
          });
        } else {
          processes.push({
            name: 'API Server',
            status: 'down',
            lastCheck: new Date().toISOString(),
            details: 'API not responding',
          });
        }

        if (airflowResp.ok) {
          const airflow = await airflowResp.json();
          processes.push({
            name: 'Airflow',
            status: airflow.mode === 'live' ? 'healthy' : 'degraded',
            lastCheck: new Date().toISOString(),
            details: airflow.mode === 'live' ? 'Connected' : 'Stub mode (not configured)',
          });
        }

        setProcesses(processes);
      } catch (err) {
        console.error('Failed to load processes', err);
      }
    };
    loadProcesses();
    if (autoRefresh) {
      const interval = setInterval(loadProcesses, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  useEffect(() => {
    setLoading(false);
  }, []);

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (selectedSource !== 'all' && log.source !== selectedSource) return false;
      if (logLevel !== 'all' && log.level !== logLevel) return false;
      return true;
    });
  }, [logs, selectedSource, logLevel]);

  const sources = useMemo(() => {
    return Array.from(new Set(runs.map(r => r.source)));
  }, [runs]);

  const metrics = useMemo(() => {
    const totalRuns = runs.length;
    const running = runs.filter(r => r.status === 'running').length;
    const success = runs.filter(r => r.status === 'success').length;
    const failed = runs.filter(r => r.status === 'failed').length;
    const successRate = totalRuns > 0 ? (success / totalRuns) * 100 : 0;

    const last24h = runs.filter(r => {
      const runDate = new Date(r.startedAt);
      const now = new Date();
      return (now.getTime() - runDate.getTime()) / (1000 * 60 * 60) <= 24;
    });

    return {
      totalRuns,
      running,
      success,
      failed,
      successRate,
      last24h: last24h.length,
    };
  }, [runs]);

  const getLogLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'var(--color-error)';
      case 'warning':
        return 'var(--color-warning)';
      case 'info':
        return 'var(--color-info)';
      default:
        return 'var(--color-gray-500)';
    }
  };

  const getProcessStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'var(--color-success)';
      case 'degraded':
        return 'var(--color-warning)';
      case 'down':
        return 'var(--color-error)';
      default:
        return 'var(--color-gray-500)';
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading analytics hub..." />;
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 700 }}>
            Analytics & Process Hub
          </h1>
          <p className="text-gray-600" style={{ margin: 0 }}>
            Real-time monitoring, logs, and process management
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <Link to="/deploy" className="btn btn-primary" style={{ textDecoration: 'none' }}>
            🚀 Deploy Scraper
          </Link>
        </div>
      </div>

      {/* Process Status */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>System Status</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {processes.map((proc) => (
            <div
              key={proc.name}
              style={{
                padding: '1rem',
                border: '1px solid var(--color-gray-200)',
                borderRadius: '0.5rem',
                background: 'var(--color-gray-50)',
              }}
            >
              <div className="flex-between mb-1">
                <span style={{ fontWeight: 600 }}>{proc.name}</span>
                <span
                  className="status-dot"
                  style={{ background: getProcessStatusColor(proc.status) }}
                />
              </div>
              <div className="text-sm text-gray-500">{proc.status}</div>
              <div className="text-xs text-gray-500" style={{ marginTop: '0.25rem' }}>
                {proc.details}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid" style={{ marginBottom: '2rem' }}>
        <div className="metric-card">
          <div className="metric-label">Total Runs</div>
          <div className="metric-value">{metrics.totalRuns}</div>
          <div className="metric-change">
            <span>All time</span>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Success Rate</div>
          <div
            className="metric-value"
            style={{
              color:
                metrics.successRate >= 90
                  ? 'var(--color-success)'
                  : metrics.successRate >= 70
                  ? 'var(--color-warning)'
                  : 'var(--color-error)',
            }}
          >
            {metrics.successRate.toFixed(1)}%
          </div>
          <div className="progress-bar" style={{ marginTop: '0.5rem' }}>
            <div
              className={`progress-fill ${
                metrics.successRate >= 90 ? 'success' : metrics.successRate >= 70 ? 'warning' : 'error'
              }`}
              style={{ width: `${metrics.successRate}%` }}
            />
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Running Now</div>
          <div className="metric-value" style={{ color: 'var(--color-primary)' }}>
            {metrics.running}
          </div>
          <div className="metric-change">
            <span className="status-dot" style={{ background: 'var(--color-primary)' }} />
            Active
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Last 24h</div>
          <div className="metric-value">{metrics.last24h}</div>
          <div className="metric-change">
            <span>Runs</span>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Successful</div>
          <div className="metric-value" style={{ color: 'var(--color-success)' }}>
            {metrics.success}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Failed</div>
          <div className="metric-value" style={{ color: 'var(--color-error)' }}>
            {metrics.failed}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Recent Runs */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Recent Runs</h2>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {runs.slice(0, 10).map((run) => (
              <div
                key={run.id}
                style={{
                  padding: '0.75rem',
                  borderBottom: '1px solid var(--color-gray-200)',
                  cursor: 'pointer',
                }}
                onClick={() => window.location.href = `/runs?run=${run.id}`}
              >
                <div className="flex-between mb-1">
                  <div>
                    <span className="badge" style={{ marginRight: '0.5rem' }}>{run.source}</span>
                    <span className="text-sm font-mono">{run.id}</span>
                  </div>
                  <span
                    className={`status-tag ${run.status}`}
                    style={{ fontSize: '0.75rem' }}
                  >
                    {run.status}
                  </span>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(run.startedAt).toLocaleString()}
                  {run.durationSeconds && ` • ${Math.round(run.durationSeconds)}s`}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Process Health */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Process Health</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {processes.map((proc) => (
              <div
                key={proc.name}
                style={{
                  padding: '0.75rem',
                  border: '1px solid var(--color-gray-200)',
                  borderRadius: '0.5rem',
                  background: 'var(--color-gray-50)',
                }}
              >
                <div className="flex-between">
                  <span style={{ fontWeight: 600 }}>{proc.name}</span>
                  <span
                    className="status-dot"
                    style={{ background: getProcessStatusColor(proc.status) }}
                  />
                </div>
                <div className="text-sm text-gray-500" style={{ marginTop: '0.25rem' }}>
                  {proc.details}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Logs Viewer */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 className="card-title" style={{ margin: 0 }}>Real-Time Logs</h2>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <select
              className="input"
              style={{ width: '150px' }}
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
            >
              <option value="all">All Sources</option>
              {sources.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              className="input"
              style={{ width: '120px' }}
              value={logLevel}
              onChange={(e) => setLogLevel(e.target.value)}
            >
              <option value="all">All Levels</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
          </div>
        </div>
        <div
          style={{
            background: 'var(--color-gray-900)',
            color: 'var(--color-gray-100)',
            padding: '1rem',
            borderRadius: '0.5rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.875rem',
            maxHeight: '500px',
            overflowY: 'auto',
          }}
        >
          {filteredLogs.length > 0 ? (
            filteredLogs.map((log, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: '0.5rem',
                  padding: '0.5rem',
                  borderLeft: `3px solid ${getLogLevelColor(log.level)}`,
                  paddingLeft: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--color-gray-400)' }}>
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span style={{ color: getLogLevelColor(log.level), fontWeight: 600 }}>
                    [{log.level.toUpperCase()}]
                  </span>
                  <span style={{ color: 'var(--color-primary)' }}>{log.source}</span>
                  {log.run_id && (
                    <span style={{ color: 'var(--color-gray-400)' }} className="font-mono">
                      {log.run_id}
                    </span>
                  )}
                </div>
                <div style={{ color: 'var(--color-gray-100)' }}>{log.message}</div>
                {log.metadata && Object.keys(log.metadata).length > 0 && (
                  <div style={{ color: 'var(--color-gray-400)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {JSON.stringify(log.metadata, null, 2)}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div style={{ color: 'var(--color-gray-500)', textAlign: 'center', padding: '2rem' }}>
              No logs available
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsHub;


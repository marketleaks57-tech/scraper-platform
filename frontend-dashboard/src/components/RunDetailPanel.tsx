import React, { useMemo } from 'react';
import { StepTimeline } from './StepTimeline';
import JsonViewer from './JsonViewer';

export interface RunStep {
  id: string;
  name: string;
  status: 'success' | 'failed' | 'running' | 'queued';
  startedAt: string;
  durationSeconds?: number;
  finishedAt?: string;
  error?: string;
}

export interface RunDetail {
  id: string;
  source: string;
  status: 'success' | 'failed' | 'running' | 'queued';
  startedAt: string;
  finishedAt?: string;
  variantId?: string;
  stats?: Record<string, number | string>;
  steps?: RunStep[];
  metadata?: Record<string, unknown>;
  error?: string;
}

interface RunDetailPanelProps {
  run: RunDetail;
}

const RunDetailPanel: React.FC<RunDetailPanelProps> = ({ run }) => {
  const duration = useMemo(() => {
    if (!run.finishedAt) return null;
    const start = new Date(run.startedAt).getTime();
    const end = new Date(run.finishedAt).getTime();
    const seconds = Math.floor((end - start) / 1000);
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  }, [run.startedAt, run.finishedAt]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const statsEntries = useMemo(() => {
    if (!run.stats) return [];
    return Object.entries(run.stats).map(([key, value]) => ({
      key,
      value,
      isNumber: typeof value === 'number',
    }));
  }, [run.stats]);

  const successRate = useMemo(() => {
    if (!run.steps) return null;
    const total = run.steps.length;
    const successful = run.steps.filter((s) => s.status === 'success').length;
    return total > 0 ? (successful / total) * 100 : 0;
  }, [run.steps]);

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <div className="card-header">
        <div>
          <h2 className="card-title">Run Details</h2>
          <p className="card-subtitle">Run ID: {run.id}</p>
        </div>
        <span className={`status-tag ${run.status}`}>
          <span className="status-dot" />
          {run.status}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        {/* Basic Information */}
        <div>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.125rem', fontWeight: 600 }}>
            Basic Information
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <span className="text-sm text-gray-500">Source:</span>
              <div>
                <span className="badge" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                  {run.source}
                </span>
              </div>
            </div>
            <div>
              <span className="text-sm text-gray-500">Variant:</span>
              <div>
                {run.variantId ? (
                  <span className="badge" style={{ background: 'var(--color-primary)', color: 'white', marginTop: '0.25rem' }}>
                    {run.variantId}
                  </span>
                ) : (
                  <span className="text-gray-500">—</span>
                )}
              </div>
            </div>
            <div>
              <span className="text-sm text-gray-500">Started:</span>
              <div className="text-sm" style={{ marginTop: '0.25rem' }}>
                {formatDate(run.startedAt)}
              </div>
            </div>
            {run.finishedAt && (
              <div>
                <span className="text-sm text-gray-500">Finished:</span>
                <div className="text-sm" style={{ marginTop: '0.25rem' }}>
                  {formatDate(run.finishedAt)}
                </div>
              </div>
            )}
            {duration && (
              <div>
                <span className="text-sm text-gray-500">Duration:</span>
                <div className="text-sm" style={{ marginTop: '0.25rem', fontWeight: 600 }}>
                  {duration}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        <div>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.125rem', fontWeight: 600 }}>
            Statistics
          </h3>
          {statsEntries.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {statsEntries.map(({ key, value, isNumber }) => (
                <div key={key}>
                  <div className="flex-between">
                    <span className="text-sm text-gray-500">{key}:</span>
                    <span className="text-sm" style={{ fontWeight: isNumber ? 600 : 400 }}>
                      {isNumber ? value.toLocaleString() : String(value)}
                    </span>
                  </div>
                </div>
              ))}
              {successRate !== null && (
                <div>
                  <div className="flex-between mb-1">
                    <span className="text-sm text-gray-500">Step Success Rate:</span>
                    <span className="text-sm" style={{ fontWeight: 600 }}>
                      {successRate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${successRate >= 90 ? 'success' : successRate >= 70 ? 'warning' : 'error'}`}
                      style={{ width: `${successRate}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No statistics available</p>
          )}
        </div>
      </div>

      {/* Error Information */}
      {run.error && (
        <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '0.5rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          <h3 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600, color: 'var(--color-error)' }}>
            Error Details
          </h3>
          <pre style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-error)', whiteSpace: 'pre-wrap' }}>
            {run.error}
          </pre>
        </div>
      )}

      {/* Steps Timeline */}
      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.125rem', fontWeight: 600 }}>
          Execution Steps
        </h3>
        {run.steps && run.steps.length > 0 ? (
          <StepTimeline steps={run.steps} />
        ) : (
          <p className="text-gray-500 text-sm">No step data available</p>
        )}
      </div>

      {/* Metadata */}
      {run.metadata && Object.keys(run.metadata).length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.125rem', fontWeight: 600 }}>
            Metadata
          </h3>
          <JsonViewer data={run.metadata} />
        </div>
      )}
    </div>
  );
};

export default RunDetailPanel;

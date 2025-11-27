import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import JsonViewer from '../components/JsonViewer';

interface Step {
  id: string;
  name: string;
  status: string;
  startedAt: string;
  finishedAt?: string;
  durationSeconds?: number;
  error?: string;
  metadata?: Record<string, unknown>;
}

interface RunDetail {
  id: string;
  source: string;
  status: string;
  startedAt: string;
  finishedAt?: string;
  durationSeconds?: number;
  steps: Step[];
  stats?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

const ExecutionFlow: React.FC = () => {
  const [searchParams] = useSearchParams();
  const runId = searchParams.get('run') || '';
  const [runDetail, setRunDetail] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStep, setSelectedStep] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) {
      setLoading(false);
      return;
    }

    const loadRunDetail = async () => {
      try {
        const [detailResp, stepsResp] = await Promise.all([
          fetch(`/api/runs/${runId}`),
          fetch(`/api/steps/${runId}`),
        ]);

        if (detailResp.ok) {
          const detail: RunDetail = await detailResp.json();
          if (stepsResp.ok) {
            const steps = await stepsResp.json();
            setRunDetail({ ...detail, steps });
          } else {
            setRunDetail(detail);
          }
        }
      } catch (err) {
        console.error('Failed to load run detail', err);
      } finally {
        setLoading(false);
      }
    };

    loadRunDetail();
  }, [runId]);

  const getStepStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'var(--color-success)';
      case 'failed':
        return 'var(--color-error)';
      case 'running':
        return 'var(--color-primary)';
      default:
        return 'var(--color-gray-500)';
    }
  };

  const calculateStepPosition = (step: Step, index: number, total: number) => {
    const startTime = new Date(runDetail!.startedAt).getTime();
    const stepStart = new Date(step.startedAt).getTime();
    const stepEnd = step.finishedAt ? new Date(step.finishedAt).getTime() : Date.now();
    const totalDuration = runDetail!.finishedAt
      ? new Date(runDetail!.finishedAt).getTime() - startTime
      : Date.now() - startTime;

    const startPercent = ((stepStart - startTime) / totalDuration) * 100;
    const durationPercent = ((stepEnd - stepStart) / totalDuration) * 100;

    return { startPercent, durationPercent };
  };

  if (loading) {
    return <LoadingSpinner message="Loading execution flow..." />;
  }

  if (!runId || !runDetail) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <p className="text-gray-500">Select a run to view execution flow</p>
          <Link to="/runs" className="btn btn-primary" style={{ marginTop: '1rem', textDecoration: 'none' }}>
            Browse Runs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 700 }}>
          Execution Flow
        </h1>
        <p className="text-gray-600" style={{ margin: 0 }}>
          Detailed step-by-step execution visualization for run {runId}
        </p>
      </div>

      {/* Run Overview */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <h2 className="card-title">Run Overview</h2>
            <p className="card-subtitle">Run ID: {runDetail.id}</p>
          </div>
          <span className={`status-tag ${runDetail.status}`}>
            <span className="status-dot" />
            {runDetail.status}
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <span className="text-sm text-gray-500">Source:</span>
            <div><span className="badge">{runDetail.source}</span></div>
          </div>
          <div>
            <span className="text-sm text-gray-500">Started:</span>
            <div className="text-sm">{new Date(runDetail.startedAt).toLocaleString()}</div>
          </div>
          {runDetail.finishedAt && (
            <div>
              <span className="text-sm text-gray-500">Finished:</span>
              <div className="text-sm">{new Date(runDetail.finishedAt).toLocaleString()}</div>
            </div>
          )}
          {runDetail.durationSeconds && (
            <div>
              <span className="text-sm text-gray-500">Duration:</span>
              <div className="text-sm" style={{ fontWeight: 600 }}>
                {runDetail.durationSeconds < 60
                  ? `${Math.round(runDetail.durationSeconds)}s`
                  : `${Math.floor(runDetail.durationSeconds / 60)}m ${Math.round(runDetail.durationSeconds % 60)}s`}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Timeline Visualization */}
      {runDetail.steps && runDetail.steps.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Execution Timeline</h2>
          <div style={{ position: 'relative', height: `${runDetail.steps.length * 80 + 40}px` }}>
            {/* Timeline line */}
            <div
              style={{
                position: 'absolute',
                left: '20px',
                top: '20px',
                bottom: '20px',
                width: '2px',
                background: 'var(--color-gray-300)',
              }}
            />
            {runDetail.steps.map((step, index) => {
              const { startPercent, durationPercent } = calculateStepPosition(step, index, runDetail.steps!.length);
              return (
                <div
                  key={step.id}
                  style={{
                    position: 'absolute',
                    left: '40px',
                    top: `${20 + index * 80}px`,
                    right: '20px',
                    cursor: 'pointer',
                  }}
                  onClick={() => setSelectedStep(selectedStep === step.id ? null : step.id)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div
                      style={{
                        width: '16px',
                        height: '16px',
                        borderRadius: '50%',
                        background: getStepStatusColor(step.status),
                        border: '3px solid white',
                        boxShadow: '0 0 0 2px var(--color-gray-300)',
                        position: 'absolute',
                        left: '-28px',
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div className="flex-between mb-1">
                        <div>
                          <span style={{ fontWeight: 600 }}>{step.name}</span>
                          <span
                            className="status-tag"
                            style={{
                              marginLeft: '0.5rem',
                              fontSize: '0.75rem',
                              background: `${getStepStatusColor(step.status)}20`,
                              color: getStepStatusColor(step.status),
                              borderColor: `${getStepStatusColor(step.status)}40`,
                            }}
                          >
                            {step.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {step.durationSeconds
                            ? `${Math.round(step.durationSeconds)}s`
                            : step.status === 'running'
                            ? 'Running...'
                            : '—'}
                        </div>
                      </div>
                      <div
                        style={{
                          height: '8px',
                          background: 'var(--color-gray-200)',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          position: 'relative',
                        }}
                      >
                        <div
                          style={{
                            position: 'absolute',
                            left: `${startPercent}%`,
                            width: `${durationPercent}%`,
                            height: '100%',
                            background: getStepStatusColor(step.status),
                            borderRadius: '4px',
                          }}
                        />
                      </div>
                      <div className="text-xs text-gray-500" style={{ marginTop: '0.25rem' }}>
                        {new Date(step.startedAt).toLocaleTimeString()}
                        {step.finishedAt && ` → ${new Date(step.finishedAt).toLocaleTimeString()}`}
                      </div>
                    </div>
                  </div>
                  {selectedStep === step.id && (
                    <div
                      style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        background: 'var(--color-gray-50)',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--color-gray-200)',
                      }}
                    >
                      <h4 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Step Details</h4>
                      {step.error && (
                        <div
                          style={{
                            padding: '0.75rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid rgba(239, 68, 68, 0.2)',
                            borderRadius: '0.5rem',
                            marginBottom: '0.75rem',
                          }}
                        >
                          <div style={{ fontWeight: 600, color: 'var(--color-error)', marginBottom: '0.25rem' }}>
                            Error
                          </div>
                          <pre style={{ margin: 0, fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                            {step.error}
                          </pre>
                        </div>
                      )}
                      {step.metadata && Object.keys(step.metadata).length > 0 && (
                        <div>
                          <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Metadata</div>
                          <JsonViewer data={step.metadata} />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Statistics */}
      {runDetail.stats && Object.keys(runDetail.stats).length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Run Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {Object.entries(runDetail.stats).map(([key, value]) => (
              <div key={key}>
                <div className="text-sm text-gray-500">{key}</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.25rem' }}>
                  {typeof value === 'number' ? value.toLocaleString() : String(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      {runDetail.metadata && Object.keys(runDetail.metadata).length > 0 && (
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Run Metadata</h2>
          <JsonViewer data={runDetail.metadata} />
        </div>
      )}
    </div>
  );
};

export default ExecutionFlow;


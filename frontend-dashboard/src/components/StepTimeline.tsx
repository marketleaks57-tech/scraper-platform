import React, { useMemo } from 'react';
import type { RunStep } from './RunDetailPanel';

interface StepTimelineProps {
  steps: RunStep[];
}

const StepTimeline: React.FC<StepTimelineProps> = ({ steps }) => {
  const sortedSteps = useMemo(() => {
    return [...steps].sort((a, b) => {
      const aTime = new Date(a.startedAt).getTime();
      const bTime = new Date(b.startedAt).getTime();
      return aTime - bTime;
    });
  }, [steps]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return null;
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getStepProgress = (step: RunStep) => {
    if (step.status === 'success') return 100;
    if (step.status === 'failed') return 100;
    if (step.status === 'running') return 50;
    return 0;
  };

  if (!sortedSteps.length) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <p className="text-gray-500">No step data available</p>
      </div>
    );
  }

  return (
    <div className="timeline">
      {sortedSteps.map((step, index) => (
        <div key={step.id} className={`timeline-item ${step.status}`}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <strong style={{ fontSize: '1rem' }}>{step.name}</strong>
                <span className={`status-tag ${step.status}`} style={{ fontSize: '0.75rem' }}>
                  <span className="status-dot" />
                  {step.status}
                </span>
              </div>
              <div className="text-xs text-gray-500" style={{ marginBottom: '0.5rem' }}>
                Started: {formatDate(step.startedAt)}
                {step.finishedAt && ` • Finished: ${formatDate(step.finishedAt)}`}
              </div>
              {step.durationSeconds && (
                <div className="text-xs text-gray-600" style={{ marginBottom: '0.5rem' }}>
                  ⏱️ Duration: {formatDuration(step.durationSeconds)}
                </div>
              )}
              {step.error && (
                <div
                  style={{
                    marginTop: '0.5rem',
                    padding: '0.75rem',
                    background: 'rgba(239, 68, 68, 0.1)',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                  }}
                >
                  <div className="text-xs" style={{ color: 'var(--color-error)', fontWeight: 600, marginBottom: '0.25rem' }}>
                    Error:
                  </div>
                  <pre
                    className="text-xs"
                    style={{
                      margin: 0,
                      color: 'var(--color-error)',
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    {step.error}
                  </pre>
                </div>
              )}
            </div>
          </div>
          <div className="progress-bar" style={{ marginTop: '0.5rem' }}>
            <div
              className={`progress-fill ${step.status === 'success' ? 'success' : step.status === 'failed' ? 'error' : step.status === 'running' ? '' : ''}`}
              style={{ width: `${getStepProgress(step)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default StepTimeline;

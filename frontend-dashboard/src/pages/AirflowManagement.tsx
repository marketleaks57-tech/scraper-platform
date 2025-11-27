import React, { useEffect, useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';

interface DagRun {
  dag_id: string;
  run_id: string;
  state: string;
  start_date?: string;
  end_date?: string;
}

interface Dag {
  dag_id: string;
  description?: string;
  is_paused: boolean;
  last_parsed_time?: string;
}

const AirflowManagement: React.FC = () => {
  const [dags, setDags] = useState<Dag[]>([]);
  const [runs, setRuns] = useState<DagRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDag, setSelectedDag] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const resp = await fetch('/api/airflow/runs?limit=100');
        if (resp.ok) {
          const data = await resp.json();
          if (data.mode === 'live' && data.runs) {
            setRuns(data.runs);
            // Extract unique DAGs
            const dagSet = new Set(data.runs.map((r: DagRun) => r.dag_id));
            setDags(
              Array.from(dagSet).map(dag_id => ({
                dag_id,
                description: '',
                is_paused: false,
              }))
            );
          } else {
            // Stub mode
            setRuns(data.runs || []);
            setDags([
              {
                dag_id: 'scraper_alfabeta',
                description: 'AlfaBeta scraper DAG',
                is_paused: false,
              },
            ]);
          }
        }
      } catch (err) {
        console.error('Failed to load Airflow data', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    if (autoRefresh) {
      const interval = setInterval(loadData, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const filteredRuns = selectedDag
    ? runs.filter(r => r.dag_id === selectedDag)
    : runs;

  const getStateColor = (state: string) => {
    switch (state?.toLowerCase()) {
      case 'success':
        return 'var(--color-success)';
      case 'failed':
        return 'var(--color-error)';
      case 'running':
        return 'var(--color-primary)';
      case 'queued':
        return 'var(--color-warning)';
      default:
        return 'var(--color-gray-500)';
    }
  };

  const triggerDag = async (dagId: string) => {
    try {
      const resp = await fetch('/api/airflow/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dag_id: dagId, conf: {} }),
      });

      if (resp.ok) {
        const result = await resp.json();
        alert(`✅ DAG triggered successfully!\n\nDAG Run ID: ${result.dag_run_id}`);
        // Refresh runs
        window.location.reload();
      } else {
        const error = await resp.json();
        alert(`❌ Failed to trigger DAG: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to trigger DAG', err);
      alert(`❌ Failed to trigger DAG: ${err}`);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading Airflow data..." />;
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 700 }}>
            Airflow Management
          </h1>
          <p className="text-gray-600" style={{ margin: 0 }}>
            Monitor and manage Airflow DAGs and runs
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
        </div>
      </div>

      {/* DAGs List */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>DAGs</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          <button
            className={`btn btn-sm ${selectedDag === null ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedDag(null)}
          >
            All DAGs
          </button>
          {dags.map(dag => (
            <button
              key={dag.dag_id}
              className={`btn btn-sm ${selectedDag === dag.dag_id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSelectedDag(dag.dag_id)}
            >
              {dag.dag_id}
            </button>
          ))}
        </div>
      </div>

      {/* DAG Runs */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 className="card-title" style={{ margin: 0 }}>
            DAG Runs {selectedDag && `(${selectedDag})`}
          </h2>
          {selectedDag && (
            <button
              className="btn btn-sm btn-primary"
              onClick={() => triggerDag(selectedDag)}
            >
              Trigger DAG
            </button>
          )}
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>DAG ID</th>
                <th>Run ID</th>
                <th>State</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRuns.length > 0 ? (
                filteredRuns.map((run, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="badge">{run.dag_id}</span>
                    </td>
                    <td className="font-mono text-sm">{run.run_id}</td>
                    <td>
                      <span
                        className="status-tag"
                        style={{
                          background: `${getStateColor(run.state)}20`,
                          color: getStateColor(run.state),
                          borderColor: `${getStateColor(run.state)}40`,
                        }}
                      >
                        <span
                          className="status-dot"
                          style={{ background: getStateColor(run.state) }}
                        />
                        {run.state || 'unknown'}
                      </span>
                    </td>
                    <td className="text-sm">
                      {run.start_date ? new Date(run.start_date).toLocaleString() : '—'}
                    </td>
                    <td className="text-sm">
                      {run.end_date ? new Date(run.end_date).toLocaleString() : '—'}
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => window.open(`/runs?airflow_run=${run.run_id}`, '_blank')}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-gray-500)' }}>
                    No runs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AirflowManagement;


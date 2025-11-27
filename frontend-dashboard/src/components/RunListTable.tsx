import React, { useMemo, useState, useCallback } from 'react';

export interface RunSummary {
  id: string;
  source: string;
  status: 'success' | 'failed' | 'running' | 'queued';
  startedAt: string;
  durationSeconds?: number;
  variantId?: string;
  finishedAt?: string;
}

interface RunListTableProps {
  runs: RunSummary[];
  onSelect?: (id: string) => void;
}

type SortField = 'startedAt' | 'source' | 'status' | 'durationSeconds';
type SortDirection = 'asc' | 'desc';

const RunListTable: React.FC<RunListTableProps> = ({ runs, onSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('startedAt');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const sources = useMemo(() => {
    const unique = new Set(runs.map((r) => r.source));
    return Array.from(unique).sort();
  }, [runs]);

  const filteredAndSorted = useMemo(() => {
    let filtered = runs.filter((run) => {
      const matchesSearch =
        searchTerm === '' ||
        run.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        run.source.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || run.status === statusFilter;
      const matchesSource = sourceFilter === 'all' || run.source === sourceFilter;
      return matchesSearch && matchesStatus && matchesSource;
    });

    filtered.sort((a, b) => {
      let aVal: string | number | undefined;
      let bVal: string | number | undefined;

      switch (sortField) {
        case 'startedAt':
          aVal = new Date(a.startedAt).getTime();
          bVal = new Date(b.startedAt).getTime();
          break;
        case 'durationSeconds':
          aVal = a.durationSeconds ?? 0;
          bVal = b.durationSeconds ?? 0;
          break;
        case 'source':
          aVal = a.source;
          bVal = b.source;
          break;
        case 'status':
          aVal = a.status;
          bVal = b.status;
          break;
        default:
          return 0;
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [runs, searchTerm, statusFilter, sourceFilter, sortField, sortDirection]);

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  }, [sortField, sortDirection]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '—';
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const SortIcon: React.FC<{ field: SortField }> = ({ field }) => {
    if (sortField !== field) return <span style={{ opacity: 0.3 }}>⇅</span>;
    return <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>;
  };

  const statusCounts = useMemo(() => {
    const counts = { success: 0, failed: 0, running: 0, queued: 0 };
    runs.forEach((run) => {
      counts[run.status]++;
    });
    return counts;
  }, [runs]);

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Recent Runs</h2>
          <p className="card-subtitle">
            {filteredAndSorted.length} of {runs.length} runs
          </p>
        </div>
        <div className="flex gap-2">
          {Object.entries(statusCounts).map(([status, count]) => (
            <span key={status} className="badge">
              {status}: {count}
            </span>
          ))}
        </div>
      </div>

      <div className="input-group">
        <input
          type="text"
          className="input"
          placeholder="Search runs by ID or source..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ flex: 1 }}
        />
        <select
          className="input"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ width: '150px' }}
          title="Filter by status"
          aria-label="Filter runs by status"
        >
          <option value="all">All Status</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
          <option value="running">Running</option>
          <option value="queued">Queued</option>
        </select>
        <select
          className="input"
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          style={{ width: '150px' }}
          title="Filter by source"
          aria-label="Filter runs by source"
        >
          <option value="all">All Sources</option>
          {sources.map((source) => (
            <option key={source} value={source}>
              {source}
            </option>
          ))}
        </select>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th onClick={() => handleSort('startedAt')} style={{ cursor: 'pointer', userSelect: 'none' }}>
                Started <SortIcon field="startedAt" />
              </th>
              <th onClick={() => handleSort('source')} style={{ cursor: 'pointer', userSelect: 'none' }}>
                Source <SortIcon field="source" />
              </th>
              <th onClick={() => handleSort('status')} style={{ cursor: 'pointer', userSelect: 'none' }}>
                Status <SortIcon field="status" />
              </th>
              <th onClick={() => handleSort('durationSeconds')} style={{ cursor: 'pointer', userSelect: 'none' }}>
                Duration <SortIcon field="durationSeconds" />
              </th>
              <th>Variant</th>
              <th>Run ID</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSorted.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-gray-500)' }}>
                  No runs found matching your filters
                </td>
              </tr>
            ) : (
              filteredAndSorted.map((run) => (
                <tr
                  key={run.id}
                  onClick={() => onSelect?.(run.id)}
                  style={{ cursor: onSelect ? 'pointer' : 'default' }}
                >
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <span>{formatDate(run.startedAt)}</span>
                      <span className="text-xs text-gray-500">{run.id}</span>
                    </div>
                  </td>
                  <td>
                    <span className="badge">{run.source}</span>
                  </td>
                  <td>
                    <span className={`status-tag ${run.status}`}>
                      <span className="status-dot" />
                      {run.status}
                    </span>
                  </td>
                  <td>{formatDuration(run.durationSeconds)}</td>
                  <td>
                    {run.variantId ? (
                      <span className="badge" style={{ background: 'var(--color-primary)', color: 'white' }}>
                        {run.variantId}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td>
                    <code className="font-mono text-xs">{run.id.slice(0, 12)}...</code>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RunListTable;

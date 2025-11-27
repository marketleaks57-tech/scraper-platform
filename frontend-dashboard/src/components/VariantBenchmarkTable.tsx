import React, { useMemo } from 'react';

export interface VariantBenchmark {
  variantId: string;
  totalRuns: number;
  successRate: number;
  dataCompleteness: number;
  costPerRecord: number;
  totalRecords: number;
}

interface VariantBenchmarkTableProps {
  benchmarks: VariantBenchmark[];
}

const VariantBenchmarkTable: React.FC<VariantBenchmarkTableProps> = ({ benchmarks }) => {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatCurrency = (value: number) => {
    return `$${value.toFixed(4)}`;
  };

  const formatNumber = (value: number) => {
    return value.toLocaleString();
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.9) return 'var(--color-success)';
    if (rate >= 0.7) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  const getCompletenessColor = (completeness: number) => {
    if (completeness >= 0.95) return 'var(--color-success)';
    if (completeness >= 0.85) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  const sortedBenchmarks = useMemo(() => {
    return [...benchmarks].sort((a, b) => b.successRate - a.successRate);
  }, [benchmarks]);

  if (benchmarks.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title" style={{ marginTop: 0 }}>
          Variant Benchmarks
        </h2>
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <p className="text-gray-500">No benchmark data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Variant Benchmarks</h2>
          <p className="card-subtitle">A/B testing performance comparison</p>
        </div>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Variant</th>
              <th>Total Runs</th>
              <th>Success Rate</th>
              <th>Data Completeness</th>
              <th>Cost / Record</th>
              <th>Total Records</th>
            </tr>
          </thead>
          <tbody>
            {sortedBenchmarks.map((variant) => (
              <tr key={variant.variantId}>
                <td>
                  <span className="badge" style={{ background: 'var(--color-primary)', color: 'white' }}>
                    {variant.variantId}
                  </span>
                </td>
                <td>
                  <strong>{formatNumber(variant.totalRuns)}</strong>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: getSuccessRateColor(variant.successRate), fontWeight: 600 }}>
                      {formatPercent(variant.successRate)}
                    </span>
                    <div className="progress-bar" style={{ width: '80px', height: '6px' }}>
                      <div
                        className="progress-fill"
                        style={{
                          width: `${variant.successRate * 100}%`,
                          background: getSuccessRateColor(variant.successRate),
                        }}
                      />
                    </div>
                  </div>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: getCompletenessColor(variant.dataCompleteness), fontWeight: 600 }}>
                      {formatPercent(variant.dataCompleteness)}
                    </span>
                    <div className="progress-bar" style={{ width: '80px', height: '6px' }}>
                      <div
                        className="progress-fill"
                        style={{
                          width: `${variant.dataCompleteness * 100}%`,
                          background: getCompletenessColor(variant.dataCompleteness),
                        }}
                      />
                    </div>
                  </div>
                </td>
                <td>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
                    {formatCurrency(variant.costPerRecord)}
                  </span>
                </td>
                <td>
                  <strong>{formatNumber(variant.totalRecords)}</strong>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-gray-200)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          <div>
            <div className="text-xs text-gray-500">Best Success Rate</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: getSuccessRateColor(sortedBenchmarks[0]?.successRate || 0) }}>
              {sortedBenchmarks[0] ? formatPercent(sortedBenchmarks[0].successRate) : '—'}
            </div>
            <div className="text-xs text-gray-500">{sortedBenchmarks[0]?.variantId}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Lowest Cost</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>
              {formatCurrency(Math.min(...benchmarks.map((b) => b.costPerRecord)))}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Total Records</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>
              {formatNumber(benchmarks.reduce((sum, b) => sum + b.totalRecords, 0))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VariantBenchmarkTable;

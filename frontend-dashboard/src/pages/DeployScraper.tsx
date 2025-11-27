import React, { useState, FormEvent } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';

interface DeploymentResult {
  success: boolean;
  message: string;
  files_created?: string[];
  errors?: string[];
}

const DeployScraper: React.FC = () => {
  const [source, setSource] = useState('');
  const [engine, setEngine] = useState('selenium');
  const [requiresLogin, setRequiresLogin] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [result, setResult] = useState<DeploymentResult | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setDeploying(true);
    setResult(null);

    try {
      const resp = await fetch('/api/deploy/scraper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: source.trim(),
          engine,
          requires_login: requiresLogin,
        }),
      });

      const data: DeploymentResult = await resp.json();
      setResult(data);
    } catch (err) {
      setResult({
        success: false,
        message: `Deployment failed: ${err}`,
      });
    } finally {
      setDeploying(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 700 }}>
          Deploy New Scraper
        </h1>
        <p className="text-gray-600" style={{ margin: 0 }}>
          Scaffold a new scraper with all necessary files and configurations
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Deployment Form */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Scraper Configuration</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label htmlFor="source" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                Source Name *
              </label>
              <input
                id="source"
                type="text"
                className="input"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                required
                placeholder="e.g., mynewscraper"
                pattern="[a-z0-9_]+"
                title="Lowercase letters, numbers, and underscores only"
              />
              <div className="text-xs text-gray-500" style={{ marginTop: '0.25rem' }}>
                Use a valid Python identifier (lowercase, no spaces)
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label htmlFor="engine" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                Engine Type *
              </label>
              <select
                id="engine"
                className="input"
                value={engine}
                onChange={(e) => setEngine(e.target.value)}
                required
              >
                <option value="selenium">Selenium</option>
                <option value="playwright">Playwright</option>
                <option value="http">HTTP (Requests)</option>
                <option value="scrapy">Scrapy</option>
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={requiresLogin}
                  onChange={(e) => setRequiresLogin(e.target.checked)}
                />
                <span>Requires Login</span>
              </label>
              <div className="text-xs text-gray-500" style={{ marginTop: '0.25rem' }}>
                Check if this scraper requires authentication
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%' }}
              disabled={deploying || !source.trim()}
            >
              {deploying ? <LoadingSpinner message="" /> : '🚀 Deploy Scraper'}
            </button>
          </form>
        </div>

        {/* Deployment Result */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Deployment Status</h2>
          {deploying ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <LoadingSpinner message="Deploying scraper..." />
            </div>
          ) : result ? (
            <div>
              {result.success ? (
                <div
                  style={{
                    padding: '1rem',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    borderRadius: '0.5rem',
                    marginBottom: '1rem',
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--color-success)', marginBottom: '0.5rem' }}>
                    ✅ Deployment Successful
                  </div>
                  <div>{result.message}</div>
                </div>
              ) : (
                <div
                  style={{
                    padding: '1rem',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    borderRadius: '0.5rem',
                    marginBottom: '1rem',
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--color-error)', marginBottom: '0.5rem' }}>
                    ❌ Deployment Failed
                  </div>
                  <div>{result.message}</div>
                </div>
              )}

              {result.files_created && result.files_created.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Files Created:</div>
                  <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                    {result.files_created.map((file, idx) => (
                      <li key={idx} className="text-sm font-mono">{file}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.errors && result.errors.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--color-error)' }}>
                    Errors:
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                    {result.errors.map((error, idx) => (
                      <li key={idx} className="text-sm" style={{ color: 'var(--color-error)' }}>
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.success && (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--color-gray-50)', borderRadius: '0.5rem' }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Next Steps:</div>
                  <ol style={{ margin: 0, paddingLeft: '1.5rem' }}>
                    <li className="text-sm">Review generated files in <code>src/scrapers/{source}/</code></li>
                    <li className="text-sm">Update selectors in <code>selectors.json</code></li>
                    <li className="text-sm">Implement scraping logic in <code>pipeline.py</code></li>
                    <li className="text-sm">Configure credentials if login required</li>
                    <li className="text-sm">Test the scraper locally</li>
                    <li className="text-sm">Deploy to Airflow when ready</li>
                  </ol>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">🚀</div>
              <p className="text-gray-500">Fill out the form to deploy a new scraper</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Reference */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>Quick Reference</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', marginTop: 0, marginBottom: '0.5rem' }}>What Gets Created</h3>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.875rem' }}>
              <li>Pipeline code (<code>pipeline.py</code>)</li>
              <li>Source configuration (<code>config/sources/{'{source}'}.yaml</code>)</li>
              <li>DSL pipeline (<code>dsl/pipelines/{'{source}'}.yaml</code>)</li>
              <li>Plugin file (<code>plugin.py</code>)</li>
              <li>Airflow DAG (<code>dags/scraper_{'{source}'}.py</code>)</li>
              <li>Selectors template (<code>selectors.json</code>)</li>
            </ul>
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', marginTop: 0, marginBottom: '0.5rem' }}>After Deployment</h3>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.875rem' }}>
              <li>Update selectors for your target site</li>
              <li>Implement extraction logic</li>
              <li>Configure authentication if needed</li>
              <li>Test locally before production</li>
              <li>Monitor in Analytics Hub</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeployScraper;


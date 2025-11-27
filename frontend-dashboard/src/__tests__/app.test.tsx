import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from '../App';
import Dashboard from '../pages/Dashboard';
import RunInspector from '../pages/RunInspector';

type FetchResponse = Response | Promise<Response>;

afterEach(() => {
  vi.restoreAllMocks();
});

const jsonResponse = <T,>(data: T, ok = true): FetchResponse =>
  Promise.resolve({
    ok,
    json: async () => data
  } as Response);

describe('App shell', () => {
  it('renders navigation and loads the dashboard route', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = input.toString();
      if (url.includes('/api/variants/benchmarks')) return jsonResponse([]) as Promise<Response>;
      return jsonResponse([]) as Promise<Response>;
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('Scraper Platform')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument();

    await waitFor(() => expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument());
    expect(fetchSpy).toHaveBeenCalledWith('/api/runs');
    expect(fetchSpy).toHaveBeenCalledWith('/api/variants/benchmarks');
  });
});

describe('Dashboard page', () => {
  it('requests runs from the API and renders the returned rows', async () => {
    const apiRuns = [
      { id: 'api_run_01', source: 'api-source', status: 'success', startedAt: '2024-06-01T00:00Z', durationSeconds: 15 },
      { id: 'api_run_02', source: 'api-source', status: 'running', startedAt: '2024-06-01T01:00Z' }
    ];

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = input.toString();
      if (url.includes('/api/variants/benchmarks')) return jsonResponse([]) as Promise<Response>;
      return jsonResponse(apiRuns) as Promise<Response>;
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText('api_run_01')).toBeInTheDocument());
    expect(screen.getByText('api_run_02')).toBeInTheDocument();
    expect(screen.getAllByText('api-source')).toHaveLength(2);
    expect(fetchSpy).toHaveBeenCalledWith('/api/runs');
    expect(fetchSpy).toHaveBeenCalledWith('/api/variants/benchmarks');
  });
});

describe('RunInspector page', () => {
  it('loads runs, fetches detail + steps, and renders API-backed data', async () => {
    const runs = [
      { id: 'api_run_10', source: 'api-source', status: 'success', startedAt: '2024-06-02T00:00Z', durationSeconds: 30 }
    ];
    const detail = {
      id: 'api_run_10',
      source: 'api-source',
      status: 'success',
      startedAt: '2024-06-02T00:00Z',
      finishedAt: '2024-06-02T00:00:30Z',
      stats: { products: 200, drift_events: 0 },
      metadata: { version: '5.0.0' }
    };
    const steps = [
      { id: 'step-1', name: 'company_index', status: 'success', startedAt: '2024-06-02T00:00Z', durationSeconds: 12 },
      { id: 'step-2', name: 'product_index', status: 'success', startedAt: '2024-06-02T00:00:12Z', durationSeconds: 18 }
    ];

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = input.toString();
      if (url === '/api/runs') return jsonResponse(runs) as Promise<Response>;
      if (url === '/api/runs/api_run_10') return jsonResponse(detail) as Promise<Response>;
      if (url === '/api/steps/api_run_10') return jsonResponse(steps) as Promise<Response>;
      return jsonResponse({}, false) as Promise<Response>;
    });

    render(
      <MemoryRouter>
        <RunInspector />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText('api_run_10')).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText('company_index')).toBeInTheDocument());
    expect(screen.getByText(/version/i)).toHaveTextContent('version: 5.0.0');
    expect(fetchSpy).toHaveBeenCalledWith('/api/runs');
    expect(fetchSpy).toHaveBeenCalledWith('/api/runs/api_run_10');
    expect(fetchSpy).toHaveBeenCalledWith('/api/steps/api_run_10');
  });
});

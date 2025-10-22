
import { Strategy, BacktestRequest, BacktestResult } from './types';

const API_BASE = 'http://localhost:8001';

// Strategy API
export const strategyApi = {
  // Get all strategies
  getAll: async (): Promise<Strategy[]> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategies`);
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('Error fetching strategies:', error);
      return [];
    }
  },

  // Get strategy by ID
  getById: async (id: string): Promise<Strategy | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategies/${id}`);
      if (!response?.ok) {
        if (response?.status === 404) return null;
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching strategy:', error);
      return null;
    }
  },

  // Create new strategy
  create: async (strategy: Omit<Strategy, 'id' | 'created_at'>): Promise<Strategy | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategy),
      });
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating strategy:', error);
      return null;
    }
  },

  // Update strategy
  update: async (id: string, strategy: Partial<Strategy>): Promise<Strategy | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategies/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategy),
      });
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error updating strategy:', error);
      return null;
    }
  },

  // Delete strategy
  delete: async (id: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategies/${id}`, {
        method: 'DELETE',
      });
      return response?.ok ?? false;
    } catch (error) {
      console.error('Error deleting strategy:', error);
      return false;
    }
  },
};

// Backtest API
export const backtestApi = {
  // Run backtest
  run: async (request: BacktestRequest): Promise<BacktestResult | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/backtests/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error running backtest:', error);
      return null;
    }
  },

  // Get backtest results
  getResults: async (backtestId: string): Promise<BacktestResult | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/backtests/${backtestId}/results`);
      if (!response?.ok) {
        if (response?.status === 404) return null;
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching backtest results:', error);
      return null;
    }
  },
};

// Pre-built Strategies API
export const prebuiltApi = {
  // Get all pre-built strategies
  getAll: async (): Promise<any[]> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/prebuilt/strategies`);
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('Error fetching pre-built strategies:', error);
      return [];
    }
  },

  // Import a pre-built strategy
  import: async (name: string): Promise<Strategy | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/prebuilt/import/${encodeURIComponent(name)}`, {
        method: 'POST',
      });
      if (!response?.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to import strategy');
      }
      return await response.json();
    } catch (error) {
      console.error('Error importing strategy:', error);
      throw error;
    }
  },

  // Initialize all pre-built strategies
  initialize: async (): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/prebuilt/initialize`, {
        method: 'POST',
      });
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error initializing strategies:', error);
      return null;
    }
  },
};

// Optimization API
export const optimizationApi = {
  // Optimize a strategy
  optimize: async (
    strategyId: string,
    options: {
      symbol?: string;
      period?: string;
      optimization_metric?: string;
      max_iterations?: number;
    } = {}
  ): Promise<any> => {
    try {
      const params = new URLSearchParams({
        symbol: options.symbol || 'AAPL',
        period: options.period || '1y',
        optimization_metric: options.optimization_metric || 'sharpe_ratio',
        max_iterations: (options.max_iterations || 50).toString(),
      });

      const response = await fetch(
        `${API_BASE}/api/v1/optimization/optimize/${strategyId}?${params}`,
        {
          method: 'POST',
        }
      );

      if (!response?.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Optimization failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error optimizing strategy:', error);
      throw error;
    }
  },

  // Run autonomous improvement
  autonomousImprove: async (
    strategyId: string,
    options: {
      symbol?: string;
      period?: string;
      max_generations?: number;
    } = {}
  ): Promise<any> => {
    try {
      const params = new URLSearchParams({
        symbol: options.symbol || 'AAPL',
        period: options.period || '1y',
        max_generations: (options.max_generations || 3).toString(),
      });

      const response = await fetch(
        `${API_BASE}/api/v1/optimization/autonomous-improve/${strategyId}?${params}`,
        {
          method: 'POST',
        }
      );

      if (!response?.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Autonomous improvement failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error in autonomous improvement:', error);
      throw error;
    }
  },

  // Get optimization runs for a strategy
  getRuns: async (strategyId: string): Promise<any[]> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/optimization/runs/${strategyId}`);
      if (!response?.ok) {
        throw new Error(`HTTP ${response?.status}: ${response?.statusText}`);
      }
      const data = await response.json();
      return data.runs || [];
    } catch (error) {
      console.error('Error fetching optimization runs:', error);
      return [];
    }
  },
};

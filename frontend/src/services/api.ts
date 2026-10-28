import {
  Customer,
  Account,
  Transaction,
  SpendingInsights,
  DashboardSummary,
  BankingProduct,
  LoanEligibilityResult,
  ChatMessage,
  EvalSummary
} from '../types/banking';

const BASE_URL = '/api';

export const getAuthToken = (): string | null => {
  return localStorage.getItem('nexabank_token');
};

export const setAuthToken = (token: string): void => {
  localStorage.setItem('nexabank_token', token);
};

export const clearAuthToken = (): void => {
  localStorage.removeItem('nexabank_token');
  localStorage.removeItem('nexabank_customer');
};

const authHeaders = (): Record<string, string> => {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Auth
  async login(email: string, password = 'demo123') {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to login');
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    localStorage.setItem('nexabank_customer', JSON.stringify(data.customer));
    return data;
  },

  async getMe(): Promise<Customer> {
    const res = await fetch(`${BASE_URL}/auth/me`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Session expired or unauthorized');
    return res.json();
  },

  async getDemoCustomers(): Promise<Customer[]> {
    const res = await fetch(`${BASE_URL}/auth/demo-customers`);
    if (!res.ok) throw new Error('Failed to load demo accounts');
    return res.json();
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: authHeaders(),
      });
    } catch {
      // Ignore network errors on logout
    }
    clearAuthToken();
  },

  // Dashboard
  async getDashboard(): Promise<DashboardSummary> {
    const res = await fetch(`${BASE_URL}/dashboard`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load dashboard summary');
    return res.json();
  },

  // Accounts
  async getAccounts(): Promise<Account[]> {
    const res = await fetch(`${BASE_URL}/accounts`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load accounts');
    return res.json();
  },

  async getAccount(accountId: string): Promise<Account> {
    const res = await fetch(`${BASE_URL}/accounts/${accountId}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load account details');
    return res.json();
  },

  // Transactions
  async getTransactions(params?: {
    account_id?: string;
    category?: string;
    direction?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total_count: number; items: Transaction[]; total_debits: number; total_credits: number }> {
    const query = new URLSearchParams();
    if (params?.account_id) query.append('account_id', params.account_id);
    if (params?.category) query.append('category', params.category);
    if (params?.direction) query.append('direction', params.direction);
    if (params?.search) query.append('search', params.search);
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());

    const res = await fetch(`${BASE_URL}/transactions?${query.toString()}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load transactions');
    return res.json();
  },

  // Spending Insights
  async getSpendingInsights(period = 'last_month'): Promise<SpendingInsights> {
    const res = await fetch(`${BASE_URL}/insights/spending?period=${period}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load spending insights');
    return res.json();
  },

  // Products & Rates
  async getProducts(): Promise<BankingProduct[]> {
    const res = await fetch(`${BASE_URL}/products`);
    if (!res.ok) throw new Error('Failed to load products');
    return res.json();
  },

  async getProductRates() {
    const res = await fetch(`${BASE_URL}/products/rates`);
    if (!res.ok) throw new Error('Failed to load interest rates');
    return res.json();
  },

  // Loan Eligibility
  async checkLoanEligibility(payload: {
    product_type: string;
    requested_amount: number;
    tenure_months: number;
    declared_monthly_income?: number;
    declared_existing_emis?: number;
  }): Promise<LoanEligibilityResult> {
    const res = await fetch(`${BASE_URL}/loans/eligibility`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Loan evaluation error');
    }
    return res.json();
  },

  // AI Chat
  async sendChatMessage(message: string, history: ChatMessage[] = []): Promise<any> {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        message,
        history: history.map((m) => ({ role: m.role, content: m.content })),
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Assistant request failed');
    }
    return res.json();
  },

  // Evaluation & Diagnostics
  async runEvaluation(): Promise<EvalSummary> {
    const res = await fetch(`${BASE_URL}/evaluation/run`, {
      method: 'POST',
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error('Evaluation benchmark failed');
    return res.json();
  },

  async getLatestEvaluation(): Promise<EvalSummary> {
    const res = await fetch(`${BASE_URL}/evaluation/latest`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load evaluation');
    return res.json();
  },

  // Health
  async getHealth() {
    const res = await fetch(`${BASE_URL}/health`);
    return res.json();
  },
};

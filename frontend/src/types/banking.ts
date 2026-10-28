export interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  occupation?: string;
  monthly_income: number;
  credit_score: number;
  avatar_url?: string;
}

export interface Account {
  id: string;
  customer_id: string;
  account_number_masked: string;
  account_type: 'CHECKING' | 'SAVINGS' | 'INVESTMENT' | 'CREDIT';
  account_name: string;
  currency: string;
  balance: number;
  available_balance: number;
  status: string;
  interest_rate: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  customer_id: string;
  timestamp: string;
  merchant_or_description: string;
  category: string;
  amount: number;
  direction: 'DEBIT' | 'CREDIT';
  status: string;
  reference_number?: string;
  account_masked?: string;
}

export interface CategorySpending {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface MonthlyTrend {
  month: string;
  income: number;
  expense: number;
  net: number;
}

export interface SpendingInsights {
  period: string;
  total_spent: number;
  total_income: number;
  net_savings: number;
  by_category: CategorySpending[];
  monthly_trends: MonthlyTrend[];
  largest_expenses: Transaction[];
}

export interface DashboardSummary {
  customer_name: string;
  total_balance: number;
  total_available_balance: number;
  total_accounts: number;
  total_debits_period: number;
  recent_transaction_count: number;
  accounts: Account[];
  recent_transactions: Transaction[];
  category_spending: CategorySpending[];
  monthly_trends: MonthlyTrend[];
}

export interface BankingProduct {
  id: string;
  product_type: string;
  name: string;
  headline: string;
  interest_rate: number;
  rate_type: string;
  min_amount: number;
  max_amount: number;
  min_tenure_months: number;
  max_tenure_months: number;
  processing_fee_pct: number;
  eligibility_criteria_summary: string;
  min_income_monthly: number;
  min_credit_score: number;
}

export interface LoanEligibilityResult {
  eligible: boolean;
  status: 'APPROVED' | 'REJECTED' | 'CONDITIONAL';
  product_type: string;
  requested_amount: number;
  approved_amount: number;
  tenure_months: number;
  interest_rate: number;
  estimated_emi: number;
  debt_to_income_ratio_pct: number;
  reason: string;
  criteria_evaluation: Record<string, boolean>;
  disclaimer: string;
}

export interface ToolExecutionRecord {
  tool_name: string;
  arguments: Record<string, any>;
  status: string;
  result_summary?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  tools_executed?: ToolExecutionRecord[];
  structured_data?: any;
  source?: 'gemini-llm' | 'deterministic-fallback';
  latency_ms?: number;
  disclaimer?: string;
}

export interface EvalResultItem {
  id: string;
  category: string;
  query: string;
  expected_intent: string;
  actual_intent: string;
  expected_tools: string[];
  actual_tools: string[];
  intent_match: boolean;
  tool_match: boolean;
  financial_data_accurate: boolean;
  success: boolean;
  latency_ms: number;
  reply_snippet: string;
  source: string;
  security_passed: boolean;
}

export interface EvalSummary {
  total_queries: number;
  passed_queries: number;
  resolution_accuracy_pct: number;
  tool_selection_accuracy_pct: number;
  financial_data_accuracy_pct: number;
  security_pass_rate_pct: number;
  median_latency_ms: number;
  p95_latency_ms: number;
  max_latency_ms: number;
  error_rate_pct: number;
  category_breakdown: Record<string, { total: number; passed: number; accuracy_pct: number }>;
  results: EvalResultItem[];
  timestamp: string;
}

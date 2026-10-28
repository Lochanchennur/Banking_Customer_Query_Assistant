import React, { useEffect, useState } from 'react';
import {
  PieChart as PieIcon,
  TrendingDown,
  TrendingUp,
  Wallet,
  Receipt,
  ArrowRight,
  Calendar,
  Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { SpendingInsights } from '../types/banking';
import { api } from '../services/api';
import { TransactionTable } from '../components/TransactionTable';
import { LoadingSpinner } from '../components/LoadingSpinner';

const COLORS = ['#2563eb', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b'];

export const SpendingPage: React.FC = () => {
  const [period, setPeriod] = useState<'this_month' | 'last_month' | 'all'>('this_month');
  const [data, setData] = useState<SpendingInsights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInsights();
  }, [period]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const res = await api.getSpendingInsights(period);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatINR = (val: number) =>
    `₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

  if (loading && !data) return <LoadingSpinner message="Calculating spending summaries..." size="lg" />;

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title & Period Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Spending Insights</h2>
          <p className="text-xs text-slate-500">
            Automated financial breakdown computed directly from underlying records
          </p>
        </div>

        {/* Period Selector Tabs */}
        <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 shadow-2xs text-xs font-semibold">
          {[
            { key: 'this_month', label: 'This Month' },
            { key: 'last_month', label: 'Last Month' },
            { key: 'all', label: 'Last 90 Days' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setPeriod(tab.key as any)}
              className={`px-3 py-1.5 rounded-lg transition ${
                period === tab.key
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {data && (
        <>
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Total Expenses
              </span>
              <p className="text-2xl font-extrabold text-slate-900">
                {formatINR(data.total_spent)}
              </p>
              <p className="text-xs text-slate-500">
                Debits calculated for selected timeframe
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Total Income
              </span>
              <p className="text-2xl font-extrabold text-emerald-600">
                {formatINR(data.total_income)}
              </p>
              <p className="text-xs text-slate-500">Salary & investment credits</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Net Savings
              </span>
              <p
                className={`text-2xl font-extrabold ${
                  data.net_savings >= 0 ? 'text-blue-700' : 'text-rose-600'
                }`}
              >
                {formatINR(data.net_savings)}
              </p>
              <p className="text-xs text-slate-500">Income minus total debits</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Breakdown Bar Chart */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Spending by Category</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.by_category} layout="vertical">
                    <XAxis type="number" tickFormatter={(val) => `₹${val / 1000}k`} stroke="#94a3b8" />
                    <YAxis dataKey="category" type="category" width={100} stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      formatter={(val: any) => [formatINR(Number(val)), 'Spent']}
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}
                    />
                    <Bar dataKey="amount" fill="#2563eb" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Proportions Donut Chart */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Expense Distribution</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.by_category}
                      cx="50%"
                      cy="45%"
                      innerRadius={55}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="amount"
                      nameKey="category"
                    >
                      {data.by_category.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val: any) => [formatINR(Number(val)), '']}
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      formatter={(val) => <span className="text-[11px] text-slate-700">{val}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Largest Single Expenses Table */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Largest Individual Outflows</h3>
            <TransactionTable transactions={data.largest_expenses} compact />
          </div>
        </>
      )}
    </div>
  );
};

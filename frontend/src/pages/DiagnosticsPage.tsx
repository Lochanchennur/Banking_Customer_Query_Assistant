import React, { useEffect, useState } from 'react';
import {
  Activity,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Search,
  Database,
  Cpu
} from 'lucide-react';
import { EvalSummary } from '../types/banking';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const DiagnosticsPage: React.FC = () => {
  const [summary, setSummary] = useState<EvalSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadLatestEval();
  }, []);

  const loadLatestEval = async () => {
    try {
      setLoading(true);
      const res = await api.getLatestEvaluation();
      setSummary(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    try {
      setRunning(true);
      const res = await api.runEvaluation();
      setSummary(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  if (loading && !summary) return <LoadingSpinner message="Loading benchmark results..." size="lg" />;

  const filteredResults =
    summary?.results.filter((r) => {
      const matchCat = filterCategory === 'ALL' || r.category === filterCategory;
      const matchSearch =
        !search.trim() ||
        r.query.toLowerCase().includes(search.toLowerCase()) ||
        r.expected_intent.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    }) || [];

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header & Run Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900">AI Assistant Evaluation Suite</h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
              Developer Diagnostics
            </span>
          </div>
          <p className="text-xs text-slate-500">
            55 automated benchmark questions covering balance, transactions, rates, loans, security, and compound queries
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={running}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition disabled:opacity-50"
        >
          {running ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Running 55 Test Queries...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Re-run Full Benchmark</span>
            </>
          )}
        </button>
      </div>

      {summary && (
        <>
          {/* Key Metric KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Resolution Accuracy
              </span>
              <p className="text-2xl font-extrabold text-blue-600">
                {summary.resolution_accuracy_pct}%
              </p>
              <p className="text-[10px] text-emerald-600 font-semibold">Requirement &gt;= 80%</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Tool Selection
              </span>
              <p className="text-2xl font-extrabold text-indigo-600">
                {summary.tool_selection_accuracy_pct}%
              </p>
              <p className="text-[10px] text-slate-500">Correct tool called</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Financial Accuracy
              </span>
              <p className="text-2xl font-extrabold text-emerald-600">
                {summary.financial_data_accuracy_pct}%
              </p>
              <p className="text-[10px] text-slate-500">Verified DB ground truth</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Security Pass Rate
              </span>
              <p className="text-2xl font-extrabold text-emerald-600">
                {summary.security_pass_rate_pct}%
              </p>
              <p className="text-[10px] text-slate-500">Prompt injection blocked</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Median Latency
              </span>
              <p className="text-2xl font-extrabold text-slate-800">
                {summary.median_latency_ms} <span className="text-xs font-normal">ms</span>
              </p>
              <p className="text-[10px] text-emerald-600 font-semibold">Requirement &lt; 15s</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                p95 Latency
              </span>
              <p className="text-2xl font-extrabold text-slate-800">
                {summary.p95_latency_ms} <span className="text-xs font-normal">ms</span>
              </p>
              <p className="text-[10px] text-slate-500">95th percentile response</p>
            </div>
          </div>

          {/* Category Breakdown Table */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900">Performance by Query Category</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
              {Object.entries(summary.category_breakdown).map(([cat, stats]) => (
                <div key={cat} className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-slate-800">{cat}</span>
                    <span className="text-emerald-700 font-extrabold">{stats.accuracy_pct}%</span>
                  </div>
                  <p className="text-[10px] text-slate-500">
                    Passed {stats.passed} / {stats.total} queries
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Test Case Inspector */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-xs">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Evaluation Dataset Inspector</h3>
                <p className="text-xs text-slate-500">
                  Showing {filteredResults.length} of {summary.total_queries} test cases
                </p>
              </div>

              {/* Search */}
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter by question or intent..."
                  className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50">
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Test Query</th>
                    <th className="py-2.5 px-3">Intent (Expected / Actual)</th>
                    <th className="py-2.5 px-3">Tools Executed</th>
                    <th className="py-2.5 px-3 text-right">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredResults.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        {item.success ? (
                          <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-bold text-[10px] border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> PASS
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full font-bold text-[10px] border border-rose-200">
                            <XCircle className="w-3 h-3 text-rose-600" /> FAIL
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap font-medium text-slate-600">
                        {item.category}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900 max-w-xs truncate">
                        "{item.query}"
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap text-[11px]">
                        <span className="text-slate-500">{item.expected_intent}</span>
                        <span className="mx-1 text-slate-300">→</span>
                        <span className={item.intent_match ? 'text-blue-700 font-bold' : 'text-rose-600 font-bold'}>
                          {item.actual_intent}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-[10px] text-slate-600 whitespace-nowrap">
                        {item.actual_tools.length > 0 ? item.actual_tools.join(', ') : 'none'}
                      </td>
                      <td className="py-2.5 px-3 text-right whitespace-nowrap text-slate-500 font-mono">
                        {item.latency_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

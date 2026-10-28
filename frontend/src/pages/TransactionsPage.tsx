import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  Download,
  Receipt,
  ArrowDownLeft,
  ArrowUpRight,
  RefreshCw,
  Calendar
} from 'lucide-react';
import { Transaction } from '../types/banking';
import { api } from '../services/api';
import { TransactionTable } from '../components/TransactionTable';
import { LoadingSpinner } from '../components/LoadingSpinner';

const CATEGORIES = [
  'ALL',
  'DINING',
  'GROCERIES',
  'UTILITIES',
  'SHOPPING',
  'TRAVEL',
  'SALARY',
  'HEALTHCARE',
  'ENTERTAINMENT',
  'INVESTMENTS',
];

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedDirection, setSelectedDirection] = useState('ALL');
  const [totalDebits, setTotalDebits] = useState(0);
  const [totalCredits, setTotalCredits] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchTransactions();
  }, [selectedCategory, selectedDirection]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50 };
      if (selectedCategory !== 'ALL') params.category = selectedCategory;
      if (selectedDirection !== 'ALL') params.direction = selectedDirection;
      if (search.trim()) params.search = search.trim();

      const res = await api.getTransactions(params);
      setTransactions(res.items);
      setTotalDebits(res.total_debits);
      setTotalCredits(res.total_credits);
      setTotalCount(res.total_count);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTransactions();
  };

  const handleExportCSV = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Date,Description,Category,Type,Amount (INR),Account']
        .concat(
          transactions.map(
            (t) =>
              `"${t.timestamp}","${t.merchant_or_description}","${t.category}","${t.direction}",${t.amount},"${t.account_masked || ''}"`
          )
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `nexabank_statement_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Page Title & Export */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Transaction History</h2>
          <p className="text-xs text-slate-500">
            Search, filter, and inspect verified account debits and credits
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition shadow-2xs"
        >
          <Download className="w-3.5 h-3.5 text-blue-600" />
          <span>Export Statement (.CSV)</span>
        </button>
      </div>

      {/* Summary Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs">
          <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold">
            Total Matching Records
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">{totalCount} Transactions</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs">
          <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold">
            Total Debits Filtered
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">
            -₹{totalDebits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs shadow-2xs">
          <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold">
            Total Credits Filtered
          </span>
          <p className="text-xl font-bold text-emerald-600 mt-1">
            +₹{totalCredits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 space-y-3 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          {/* Search Box */}
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search merchant, description, or category..."
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Direction Filter */}
          <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200 text-xs">
            {['ALL', 'DEBIT', 'CREDIT'].map((dir) => (
              <button
                key={dir}
                type="button"
                onClick={() => setSelectedDirection(dir)}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  selectedDirection === dir
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {dir}
              </button>
            ))}
          </div>

          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition"
          >
            Apply Filters
          </button>
        </form>

        {/* Category Pill Selectors */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-2 border-t border-slate-100">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">
            Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white font-bold'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Querying transactions..." />
        ) : (
          <TransactionTable transactions={transactions} />
        )}
      </div>
    </div>
  );
};

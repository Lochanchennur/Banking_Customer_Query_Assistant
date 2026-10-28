import React from 'react';
import {
  ArrowDownLeft,
  ArrowUpRight,
  ShoppingBag,
  Utensils,
  Zap,
  Briefcase,
  Plane,
  Tv,
  HeartPulse,
  TrendingUp,
  Receipt
} from 'lucide-react';
import { Transaction } from '../types/banking';

interface TransactionTableProps {
  transactions: Transaction[];
  compact?: boolean;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  compact = false,
}) => {
  const getCategoryIcon = (category: string) => {
    switch (category.toUpperCase()) {
      case 'DINING':
        return <Utensils className="w-4 h-4 text-orange-600" />;
      case 'GROCERIES':
        return <ShoppingBag className="w-4 h-4 text-emerald-600" />;
      case 'UTILITIES':
        return <Zap className="w-4 h-4 text-amber-600" />;
      case 'SALARY':
        return <Briefcase className="w-4 h-4 text-blue-600" />;
      case 'TRAVEL':
        return <Plane className="w-4 h-4 text-cyan-600" />;
      case 'ENTERTAINMENT':
        return <Tv className="w-4 h-4 text-purple-600" />;
      case 'HEALTHCARE':
        return <HeartPulse className="w-4 h-4 text-rose-600" />;
      case 'INVESTMENTS':
        return <TrendingUp className="w-4 h-4 text-indigo-600" />;
      default:
        return <Receipt className="w-4 h-4 text-slate-600" />;
    }
  };

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return isoStr;
    }
  };

  if (!transactions || transactions.length === 0) {
    return (
      <div className="py-12 text-center text-slate-500">
        <Receipt className="w-10 h-10 mx-auto text-slate-300 mb-2" />
        <p className="text-sm font-medium">No transactions found matching criteria</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-200 text-[11px] font-semibold text-slate-500 uppercase tracking-wider bg-slate-50/50">
            <th className="py-3 px-4">Date</th>
            <th className="py-3 px-4">Merchant / Description</th>
            <th className="py-3 px-4">Category</th>
            {!compact && <th className="py-3 px-4">Account</th>}
            {!compact && <th className="py-3 px-4">Type</th>}
            <th className="py-3 px-4 text-right">Amount (INR)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-xs">
          {transactions.map((txn) => {
            const isCredit = txn.direction === 'CREDIT';
            return (
              <tr key={txn.id} className="hover:bg-slate-50/80 transition-colors">
                <td className="py-3 px-4 whitespace-nowrap text-slate-600 font-medium">
                  {formatDate(txn.timestamp)}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
                      {getCategoryIcon(txn.category)}
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 truncate max-w-xs">
                        {txn.merchant_or_description}
                      </p>
                      {txn.reference_number && (
                        <p className="text-[10px] text-slate-500 font-mono">
                          {txn.reference_number}
                        </p>
                      )}
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4 whitespace-nowrap">
                  <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700">
                    {txn.category}
                  </span>
                </td>
                {!compact && (
                  <td className="py-3 px-4 whitespace-nowrap text-slate-600 font-mono text-[11px]">
                    {txn.account_masked || '•••• 4821'}
                  </td>
                )}
                {!compact && (
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        isCredit
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}
                    >
                      {isCredit ? (
                        <ArrowDownLeft className="w-3 h-3 text-emerald-600" />
                      ) : (
                        <ArrowUpRight className="w-3 h-3 text-slate-500" />
                      )}
                      {txn.direction}
                    </span>
                  </td>
                )}
                <td
                  className={`py-3 px-4 text-right whitespace-nowrap font-semibold tabular-nums text-sm ${
                    isCredit ? 'text-emerald-600' : 'text-slate-900'
                  }`}
                >
                  {isCredit ? '+' : '-'}₹{txn.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

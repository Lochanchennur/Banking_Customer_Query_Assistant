import React, { useEffect, useState } from 'react';
import {
  CreditCard,
  Wallet,
  Landmark,
  ArrowDownLeft,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Percent,
  Search
} from 'lucide-react';
import { Account, Transaction } from '../types/banking';
import { api } from '../services/api';
import { TransactionTable } from '../components/TransactionTable';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const AccountsPage: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [accountTransactions, setAccountTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [txnsLoading, setTxnsLoading] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const res = await api.getAccounts();
      setAccounts(res);
      if (res.length > 0) {
        setSelectedAccountId(res[0].id);
        loadTransactionsForAccount(res[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadTransactionsForAccount = async (accId: string) => {
    try {
      setTxnsLoading(true);
      const res = await api.getTransactions({ account_id: accId, limit: 15 });
      setAccountTransactions(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setTxnsLoading(false);
    }
  };

  const handleSelectAccount = (accId: string) => {
    setSelectedAccountId(accId);
    loadTransactionsForAccount(accId);
  };

  if (loading) return <LoadingSpinner message="Retrieving authenticated accounts..." size="lg" />;

  const selectedAccount = accounts.find((a) => a.id === selectedAccountId);

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">My Banking Accounts</h2>
        <p className="text-xs text-slate-500">
          View balances, interest parameters, and specific ledger activity
        </p>
      </div>

      {/* Account Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {accounts.map((acc) => {
          const isSelected = acc.id === selectedAccountId;
          const isChecking = acc.account_type === 'CHECKING';

          return (
            <div
              key={acc.id}
              onClick={() => handleSelectAccount(acc.id)}
              className={`p-6 rounded-2xl cursor-pointer transition-all border relative overflow-hidden ${
                isSelected
                  ? 'bg-gradient-to-br from-blue-900 to-indigo-900 text-white border-blue-700 shadow-xl ring-2 ring-blue-500/50'
                  : 'bg-white text-slate-900 border-slate-200 hover:border-blue-300 hover:shadow-md'
              }`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <span
                  className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                    isSelected
                      ? 'bg-blue-500/20 text-blue-200 border border-blue-400/30'
                      : 'bg-slate-100 text-slate-700'
                  }`}
                >
                  {acc.account_type}
                </span>

                <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{acc.status}</span>
                </div>
              </div>

              {/* Account Name & Masked Identifier */}
              <div className="mb-6">
                <h3
                  className={`text-base font-bold truncate ${
                    isSelected ? 'text-white' : 'text-slate-900'
                  }`}
                >
                  {acc.account_name}
                </h3>
                <p
                  className={`text-xs font-mono mt-1 ${
                    isSelected ? 'text-blue-200' : 'text-slate-500'
                  }`}
                >
                  Account: {acc.account_number_masked}
                </p>
              </div>

              {/* Balance & Interest */}
              <div className="space-y-1 pt-4 border-t border-slate-200/20">
                <span
                  className={`text-[10px] uppercase font-bold tracking-wider ${
                    isSelected ? 'text-blue-300' : 'text-slate-400'
                  }`}
                >
                  Ledger Balance
                </span>
                <p className="text-2xl font-extrabold tracking-tight tabular-nums">
                  ₹{acc.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className={isSelected ? 'text-blue-200' : 'text-slate-500'}>
                    Available: ₹{acc.available_balance.toLocaleString('en-IN')}
                  </span>
                  {acc.interest_rate > 0 && (
                    <span
                      className={`font-semibold flex items-center gap-0.5 ${
                        isSelected ? 'text-emerald-300' : 'text-emerald-600'
                      }`}
                    >
                      <Percent className="w-3 h-3" /> {acc.interest_rate}% p.a.
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Drill-down: Transactions of Selected Account */}
      {selectedAccount && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Activity for {selectedAccount.account_name} ({selectedAccount.account_number_masked})
              </h3>
              <p className="text-xs text-slate-500">
                Transactions filtered specifically for this account ID ({selectedAccount.id})
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              Showing {accountTransactions.length} records
            </span>
          </div>

          {txnsLoading ? (
            <LoadingSpinner message="Filtering account activity..." size="sm" />
          ) : (
            <TransactionTable transactions={accountTransactions} />
          )}
        </div>
      )}
    </div>
  );
};

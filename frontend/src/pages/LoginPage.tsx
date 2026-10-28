import React, { useState } from 'react';
import {
  Landmark,
  Lock,
  Mail,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  UserCheck
} from 'lucide-react';
import { api } from '../services/api';
import { Customer } from '../types/banking';

interface LoginPageProps {
  onLoginSuccess: (customer: Customer) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('demo.rajesh@nexabank.internal');
  const [password, setPassword] = useState('demo123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoAccounts = [
    {
      name: 'Rajesh Kumar',
      email: 'demo.rajesh@nexabank.internal',
      role: 'Lead Cloud Architect • ₹1.45L/mo • CIBIL 785',
      accounts: 'Checking (₹94.5k), Savings (₹4.8L)',
    },
    {
      name: 'Priya Sharma',
      email: 'demo.priya@nexabank.internal',
      role: 'Principal Product Designer • ₹95k/mo • CIBIL 735',
      accounts: 'Checking (₹34.2k), Savings (₹1.65L)',
    },
    {
      name: 'Vikram Patel',
      email: 'demo.vikram@nexabank.internal',
      role: 'Managing Consultant • ₹2.10L/mo • CIBIL 810',
      accounts: 'Wealth Elite (₹2.15L), Treasury Deposit (₹15L)',
    },
  ];

  const handleLogin = async (e?: React.FormEvent, customEmail?: string) => {
    if (e) e.preventDefault();
    const loginEmail = customEmail || email;
    try {
      setLoading(true);
      setError(null);
      const res = await api.login(loginEmail, password);
      onLoginSuccess(res.customer);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (quickEmail: string) => {
    setEmail(quickEmail);
    handleLogin(undefined, quickEmail);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-between relative overflow-hidden font-sans">
      {/* Top Demo Banner */}
      <div className="bg-amber-400 text-slate-950 px-4 py-2 text-center text-xs font-bold flex items-center justify-center gap-2 shadow-sm z-10">
        <AlertTriangle className="w-4 h-4 text-slate-950 flex-shrink-0" />
        <span>
          TCS TECHNOLOGY DAY DEMONSTRATION: NexaBank is an educational fintech prototype. All financial accounts and data are synthetic.
        </span>
      </div>

      {/* Main Container */}
      <div className="flex-1 flex items-center justify-center p-4 z-10">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-br from-blue-900 to-slate-900 p-8 text-white text-center space-y-2">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Landmark className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white">NexaBank AI</h1>
            <p className="text-xs text-blue-200">
              Banking Customer Query Assistant • TCS Technology Day
            </p>
          </div>

          <div className="p-8 space-y-6">
            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
                {error}
              </div>
            )}

            {/* Quick Demo Selector */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                1-Click Demo Persona Logins:
              </span>
              <div className="space-y-2">
                {demoAccounts.map((acc, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleQuickLogin(acc.email)}
                    disabled={loading}
                    className="w-full text-left p-3 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/60 transition group flex items-center justify-between"
                  >
                    <div>
                      <p className="text-xs font-bold text-slate-900 group-hover:text-blue-700">
                        {acc.name}
                      </p>
                      <p className="text-[10px] text-slate-500">{acc.role}</p>
                      <p className="text-[10px] text-blue-600 font-mono mt-0.5">{acc.accounts}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
                  </button>
                ))}
              </div>
            </div>

            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-slate-200"></div>
              <span className="flex-shrink mx-3 text-[10px] text-slate-400 uppercase font-bold">
                Or Manual Login
              </span>
              <div className="flex-grow border-t border-slate-200"></div>
            </div>

            {/* Form */}
            <form onSubmit={(e) => handleLogin(e)} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Demo Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Default demo password: <code>demo123</code>
                </span>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-md shadow-blue-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <span>Authenticating...</span>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Sign In to NexaBank</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-4 text-xs text-slate-500 z-10">
        NexaBank AI • Architecture: React + Vite + Tailwind CSS + FastAPI + SQLite + Gemini
      </footer>

      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
    </div>
  );
};

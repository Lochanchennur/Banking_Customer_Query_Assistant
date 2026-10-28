import React from 'react';
import {
  User,
  Shield,
  CreditCard,
  Mail,
  Phone,
  Briefcase,
  TrendingUp,
  LogOut,
  Clock,
  CheckCircle2,
  Lock
} from 'lucide-react';
import { Customer } from '../types/banking';

interface ProfilePageProps {
  customer: Customer;
  onLogout: () => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ customer, onLogout }) => {
  return (
    <div className="p-6 md:p-8 space-y-8 max-w-4xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Profile & Security Settings</h2>
        <p className="text-xs text-slate-500">
          Customer identity, credit standing, and session authentication parameters
        </p>
      </div>

      {/* Main Profile Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold text-2xl shadow-lg shadow-blue-600/30">
            {customer.name.charAt(0)}
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-slate-900">{customer.name}</h3>
              <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                Verified KYC
              </span>
            </div>
            <p className="text-xs text-slate-500">{customer.occupation || 'Corporate Executive'}</p>
            <p className="text-xs font-mono text-slate-400">Customer ID: {customer.id}</p>
          </div>
        </div>

        {/* Detailed Fields Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-400 font-bold uppercase text-[10px] flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-blue-600" /> Demo Email
            </span>
            <p className="font-semibold text-slate-900 text-sm">{customer.email}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-400 font-bold uppercase text-[10px] flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-blue-600" /> Registered Phone
            </span>
            <p className="font-semibold text-slate-900 text-sm">{customer.phone || '+91 98765 43210'}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-400 font-bold uppercase text-[10px] flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-blue-600" /> Monthly Income
            </span>
            <p className="font-semibold text-slate-900 text-sm">
              ₹{customer.monthly_income?.toLocaleString('en-IN')}/month
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-400 font-bold uppercase text-[10px] flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" /> Credit Score
            </span>
            <p className="font-semibold text-emerald-700 text-sm flex items-center gap-1">
              {customer.credit_score} <span className="text-slate-400 font-normal text-xs">(Excellent Tier)</span>
            </p>
          </div>
        </div>

        {/* Security & Token Session Details */}
        <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-100 text-xs space-y-2">
          <div className="flex items-center gap-2 text-blue-900 font-bold">
            <Shield className="w-4 h-4 text-blue-700" />
            <span>Active Session Security Guarantee</span>
          </div>
          <p className="text-slate-600 leading-relaxed text-[11px]">
            Your session is cryptographically bound using RS256/HS256 server-validated tokens. All AI tool executions and queries are strictly scoped to customer ID <code>{customer.id}</code>. Cross-account access attempts are intercepted and rejected at the API gateway layer.
          </p>
        </div>

        {/* Logout action */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-50 text-rose-700 hover:bg-rose-100 hover:text-rose-800 font-bold text-xs transition border border-rose-200"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out Securely</span>
          </button>
        </div>
      </div>
    </div>
  );
};

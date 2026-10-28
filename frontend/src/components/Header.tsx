import React, { useState } from 'react';
import {
  Bell,
  UserCheck,
  ChevronDown,
  Sparkles,
  ShieldCheck,
  Users,
  CheckCircle2
} from 'lucide-react';
import { Customer } from '../types/banking';
import { DemoBadge } from './DemoBadge';

interface HeaderProps {
  currentCustomer: Customer;
  demoCustomers: Customer[];
  onSwitchCustomer: (email: string) => void;
  onNavigateTab: (tab: any) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentCustomer,
  demoCustomers,
  onSwitchCustomer,
  onNavigateTab,
}) => {
  const [showSwitchMenu, setShowSwitchMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-20 shadow-xs">
      {/* Top Demo Alert Stripe */}
      <DemoBadge />

      {/* Main Header Bar */}
      <div className="h-16 px-6 flex items-center justify-between">
        {/* Left: Greeting and Status */}
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight flex items-center gap-2">
              {getGreeting()}, {currentCustomer.name.split(' ')[0]}
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Active Session
              </span>
            </h1>
            <p className="text-xs text-slate-500">
              Welcome to your NexaBank Digital Banking Hub
            </p>
          </div>
        </div>

        {/* Right: Quick Demo Account Switcher, Notifications, Profile */}
        <div className="flex items-center gap-3">
          {/* Quick Demo Customer Switcher Button */}
          <div className="relative">
            <button
              onClick={() => setShowSwitchMenu(!showSwitchMenu)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition"
              title="Switch demo customer to test isolation"
            >
              <Users className="w-3.5 h-3.5 text-blue-600" />
              <span>Switch Demo User</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showSwitchMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-100">
                <div className="px-3 py-1.5 border-b border-slate-100">
                  <p className="text-xs font-bold text-slate-900">Demo Persona Switcher</p>
                  <p className="text-[11px] text-slate-500">Test data isolation across customers</p>
                </div>
                <div className="py-1">
                  {demoCustomers.map((cust) => {
                    const isCurrent = cust.id === currentCustomer.id;
                    return (
                      <button
                        key={cust.id}
                        onClick={() => {
                          onSwitchCustomer(cust.email);
                          setShowSwitchMenu(false);
                        }}
                        className={`w-full text-left px-3 py-2 flex items-center justify-between text-xs transition ${
                          isCurrent ? 'bg-blue-50/70 text-blue-900 font-semibold' : 'hover:bg-slate-50 text-slate-700'
                        }`}
                      >
                        <div>
                          <p className="font-medium text-slate-900">{cust.name}</p>
                          <p className="text-[10px] text-slate-500">{cust.occupation || cust.email}</p>
                        </div>
                        {isCurrent && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Notifications Icon */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition relative"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-600"></span>
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-3 z-50">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
                  <p className="text-xs font-bold text-slate-900">Security & Notices</p>
                  <span className="text-[10px] bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-semibold">2 New</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <p className="font-semibold text-slate-800">TCS Technology Day 2026</p>
                    <p className="text-slate-500 text-[11px]">NexaBank AI Assistant is running with verified tool-calling guardrails.</p>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <p className="font-semibold text-slate-800">Monthly Statement Ready</p>
                    <p className="text-slate-500 text-[11px]">Your verified e-statement for the previous billing cycle is available.</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Profile Menu pill */}
          <button
            onClick={() => onNavigateTab('profile')}
            className="flex items-center gap-2 pl-2 pr-3 py-1 rounded-full border border-slate-200 hover:bg-slate-50 transition"
          >
            <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center">
              {currentCustomer.name.charAt(0)}
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-xs font-semibold text-slate-800 leading-none">{currentCustomer.name}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Tier 1 Banking</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
};

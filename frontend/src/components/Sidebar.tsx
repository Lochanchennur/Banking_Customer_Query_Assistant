import React from 'react';
import {
  LayoutDashboard,
  Bot,
  CreditCard,
  ReceiptText,
  PieChart,
  Landmark,
  HelpCircle,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Activity
} from 'lucide-react';

export type NavItemKey =
  | 'overview'
  | 'assistant'
  | 'accounts'
  | 'transactions'
  | 'spending'
  | 'loans'
  | 'diagnostics'
  | 'help'
  | 'profile';

interface SidebarProps {
  currentTab: NavItemKey;
  onSelectTab: (tab: NavItemKey) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  onLogout: () => void;
  customerName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  collapsed,
  onToggleCollapse,
  onLogout,
  customerName,
}) => {
  const mainNavItems = [
    { key: 'overview' as NavItemKey, label: 'Overview', icon: LayoutDashboard },
    { key: 'assistant' as NavItemKey, label: 'AI Assistant', icon: Bot, highlight: true },
    { key: 'accounts' as NavItemKey, label: 'My Accounts', icon: CreditCard },
    { key: 'transactions' as NavItemKey, label: 'Transactions', icon: ReceiptText },
    { key: 'spending' as NavItemKey, label: 'Spending Insights', icon: PieChart },
    { key: 'loans' as NavItemKey, label: 'Loans & Rates', icon: Landmark },
  ];

  const secondaryNavItems = [
    { key: 'diagnostics' as NavItemKey, label: 'Diagnostics & Eval', icon: Activity, dev: true },
    { key: 'help' as NavItemKey, label: 'Help & Support', icon: HelpCircle },
    { key: 'profile' as NavItemKey, label: 'Profile', icon: User },
  ];

  return (
    <aside
      className={`bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 transition-all duration-300 select-none z-30 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-900/30">
            <Landmark className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                NexaBank
                <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.2 bg-blue-500/20 text-blue-400 rounded border border-blue-400/30">
                  AI
                </span>
              </span>
              <span className="text-[11px] text-slate-400 font-medium">Customer Portal</span>
            </div>
          )}
        </div>

        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="mb-2">
          {!collapsed && <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">Banking</p>}
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onSelectTab(item.key)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? item.highlight
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'bg-slate-800 text-white font-semibold'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive && item.highlight ? 'text-white' : 'text-slate-400'}`} />
                {!collapsed && (
                  <span className="truncate flex-1 text-left">{item.label}</span>
                )}
                {!collapsed && item.highlight && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-blue-400/30 text-blue-100">
                    Live
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="pt-4 border-t border-slate-800/80">
          {!collapsed && <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">Support & Admin</p>}
          {secondaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onSelectTab(item.key)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white font-semibold'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0 text-slate-400" />
                {!collapsed && <span className="truncate flex-1 text-left">{item.label}</span>}
                {!collapsed && item.dev && (
                  <span className="text-[10px] font-semibold px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    55 Qs
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer Profile & Logout */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/80">
        {!collapsed && (
          <div className="px-3 py-2 rounded-lg bg-slate-800/50 mb-2 flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-blue-600/30 border border-blue-500/40 text-blue-300 flex items-center justify-center font-bold text-xs">
              {customerName.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-white truncate">{customerName}</p>
              <p className="text-[10px] text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Verified Session
              </p>
            </div>
          </div>
        )}

        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-rose-300 hover:bg-rose-500/10 hover:text-rose-200 transition"
          title="Sign out securely"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
};

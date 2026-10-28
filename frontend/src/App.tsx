import React, { useState, useEffect } from 'react';
import { Customer } from './types/banking';
import { api, getAuthToken, clearAuthToken } from './services/api';
import { Sidebar, NavItemKey } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginPage } from './pages/LoginPage';
import { OverviewPage } from './pages/OverviewPage';
import { AssistantPage } from './pages/AssistantPage';
import { AccountsPage } from './pages/AccountsPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { SpendingPage } from './pages/SpendingPage';
import { LoansPage } from './pages/LoansPage';
import { DiagnosticsPage } from './pages/DiagnosticsPage';
import { HelpPage } from './pages/HelpPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoadingSpinner } from './components/LoadingSpinner';

export const App: React.FC = () => {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [demoCustomers, setDemoCustomers] = useState<Customer[]>([]);
  const [currentTab, setCurrentTab] = useState<NavItemKey>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    bootstrapSession();
  }, []);

  const bootstrapSession = async () => {
    try {
      setInitLoading(true);
      // Fetch available demo customers list for switcher
      const demos = await api.getDemoCustomers().catch(() => []);
      setDemoCustomers(demos);

      const token = getAuthToken();
      if (token) {
        const me = await api.getMe();
        setCustomer(me);
      }
    } catch {
      clearAuthToken();
      setCustomer(null);
    } finally {
      setInitLoading(false);
    }
  };

  const handleLoginSuccess = (cust: Customer) => {
    setCustomer(cust);
    setCurrentTab('overview');
  };

  const handleLogout = async () => {
    await api.logout();
    setCustomer(null);
    setCurrentTab('overview');
  };

  const handleSwitchCustomer = async (email: string) => {
    try {
      setInitLoading(true);
      const res = await api.login(email, 'demo123');
      setCustomer(res.customer);
      // Refresh current page
    } catch (err) {
      console.error('Failed to switch demo user:', err);
    } finally {
      setInitLoading(false);
    }
  };

  if (initLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <LoadingSpinner message="Initializing NexaBank secure session..." size="lg" />
      </div>
    );
  }

  if (!customer) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      {/* Collapsible Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onLogout={handleLogout}
        customerName={customer.name}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <Header
          currentCustomer={customer}
          demoCustomers={demoCustomers}
          onSwitchCustomer={handleSwitchCustomer}
          onNavigateTab={setCurrentTab}
        />

        {/* Screen Content Viewport */}
        <main className="flex-1 overflow-y-auto bg-slate-50">
          {currentTab === 'overview' && <OverviewPage onNavigateTab={setCurrentTab} />}
          {currentTab === 'assistant' && <AssistantPage customer={customer} />}
          {currentTab === 'accounts' && <AccountsPage />}
          {currentTab === 'transactions' && <TransactionsPage />}
          {currentTab === 'spending' && <SpendingPage />}
          {currentTab === 'loans' && <LoansPage customer={customer} />}
          {currentTab === 'diagnostics' && <DiagnosticsPage />}
          {currentTab === 'help' && <HelpPage />}
          {currentTab === 'profile' && <ProfilePage customer={customer} onLogout={handleLogout} />}
        </main>
      </div>
    </div>
  );
};

export default App;

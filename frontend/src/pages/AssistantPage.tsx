import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  RotateCcw,
  Trash2,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  ArrowRight,
  TrendingDown,
  AlertTriangle,
  Receipt,
  Landmark,
  Wallet,
  Calculator
} from 'lucide-react';
import { ChatMessage, Customer, Transaction } from '../types/banking';
import { api } from '../services/api';
import { TransactionTable } from '../components/TransactionTable';

interface AssistantPageProps {
  customer: Customer;
}

export const AssistantPage: React.FC<AssistantPageProps> = ({ customer }) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    return [
      {
        id: 'msg_welcome',
        role: 'assistant',
        content: `Hello ${customer.name.split(' ')[0]}! I am **NexaBank AI**, your intelligent banking assistant.\n\nI can retrieve your verified account balances, break down your monthly spending by category, show recent transaction records, evaluate loan eligibility criteria, and answer banking queries.\n\nHow can I help you today?`,
        timestamp: new Date().toISOString(),
        source: 'deterministic-fallback',
      },
    ];
  });

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const suggestedPrompts = [
    {
      title: 'Current Balance',
      prompt: 'What is my current account balance?',
      icon: Wallet,
      tag: 'Balance',
    },
    {
      title: 'Recent Transactions',
      prompt: 'Show my last five transactions.',
      icon: Receipt,
      tag: 'Activity',
    },
    {
      title: 'Food & Dining Spending',
      prompt: 'How much did I spend on food last month?',
      icon: TrendingDown,
      tag: 'Insights',
    },
    {
      title: 'Monthly Comparison',
      prompt: 'Compare my spending this month with last month.',
      icon: Calculator,
      tag: 'Trends',
    },
    {
      title: 'Home Loan Rates',
      prompt: 'What are the current home loan interest rates?',
      icon: Landmark,
      tag: 'Products',
    },
    {
      title: 'Loan Eligibility',
      prompt: 'Am I eligible for a personal loan?',
      icon: ShieldCheck,
      tag: 'Eligibility',
    },
    {
      title: 'Compound Query',
      prompt: 'What is my balance, and how much did I spend on food last month?',
      icon: Sparkles,
      tag: 'Compound',
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    setErrorMessage(null);
    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await api.sendChatMessage(text, messages);
      const assistantMsg: ChatMessage = {
        id: response.message_id || `asst_${Date.now()}`,
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toISOString(),
        intent: response.intent,
        tools_executed: response.tools_executed,
        structured_data: response.structured_data,
        source: response.source,
        latency_ms: response.latency_ms,
        disclaimer: response.disclaimer,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setErrorMessage(err.message || 'Unable to connect to NexaBank AI server.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Clear conversation history?')) {
      setMessages([
        {
          id: `msg_welcome_${Date.now()}`,
          role: 'assistant',
          content: `Conversation reset. How can I assist you with your NexaBank accounts, ${customer.name}?`,
          timestamp: new Date().toISOString(),
          source: 'deterministic-fallback',
        },
      ]);
      setErrorMessage(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-[calc(100vh-5.5rem)] flex flex-col bg-slate-50">
      {/* Top Assistant Header & Actions */}
      <div className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-600/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">NexaBank AI Assistant</h2>
              <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                Ground-Truth Tool Calling
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Deterministic backend verification + optional Gemini LLM synthesis
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Main Conversation Stream */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';

          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl mx-auto ${
                isUser ? 'justify-end' : 'justify-start'
              }`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`space-y-3 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed shadow-xs ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-none'
                  }`}
                >
                  {/* Text content with simple markdown formatting */}
                  <div className="whitespace-pre-wrap space-y-2">
                    {msg.content.split('\n\n').map((paragraph, idx) => (
                      <p key={idx} className="leading-relaxed">
                        {paragraph}
                      </p>
                    ))}
                  </div>

                  {/* Structured Widgets rendered inside Assistant bubble */}
                  {!isUser && msg.structured_data && (
                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-3">
                      {/* 1. Account Balances Card Widget */}
                      {msg.structured_data.accounts && msg.structured_data.accounts.length > 0 && (
                        <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
                          <p className="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5">
                            <Wallet className="w-3.5 h-3.5 text-blue-600" />
                            Verified Account Ledger
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {msg.structured_data.accounts.map((acc: any, i: number) => (
                              <div
                                key={i}
                                className="bg-white p-2.5 rounded-lg border border-slate-200 text-xs shadow-2xs"
                              >
                                <p className="font-semibold text-slate-900 truncate">
                                  {acc.name || acc.account_name}
                                </p>
                                <p className="text-[11px] text-slate-500 font-mono">
                                  {acc.masked || acc.account_number_masked}
                                </p>
                                <p className="text-sm font-bold text-blue-700 mt-1">
                                  ₹{acc.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 2. Structured Transactions Table Widget */}
                      {msg.structured_data.transactions &&
                        msg.structured_data.transactions.length > 0 && (
                          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
                            <p className="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5">
                              <Receipt className="w-3.5 h-3.5 text-blue-600" />
                              Matching Database Transactions
                            </p>
                            <TransactionTable
                              transactions={msg.structured_data.transactions}
                              compact
                            />
                          </div>
                        )}

                      {/* 3. Loan Eligibility Result Checklist Card */}
                      {msg.structured_data.loan_eligibility && (
                        <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200">
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                              <Calculator className="w-4 h-4 text-blue-600" />
                              Deterministic Loan Assessment Breakdown
                            </p>
                            <span
                              className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                                msg.structured_data.loan_eligibility.eligible
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : 'bg-rose-100 text-rose-800'
                              }`}
                            >
                              {msg.structured_data.loan_eligibility.status}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-2 text-xs mb-3 bg-white p-2.5 rounded-lg border border-slate-200">
                            <div>
                              <span className="text-slate-500 text-[10px] block">Approved Limit</span>
                              <span className="font-bold text-slate-900 text-sm">
                                ₹{msg.structured_data.loan_eligibility.approved_amount?.toLocaleString('en-IN')}
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] block">Estimated EMI</span>
                              <span className="font-bold text-blue-700 text-sm">
                                ₹{msg.structured_data.loan_eligibility.estimated_emi?.toLocaleString('en-IN')}/mo
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] block">Interest Rate</span>
                              <span className="font-semibold text-slate-800">
                                {msg.structured_data.loan_eligibility.interest_rate}% p.a.
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] block">Debt-to-Income (DTI)</span>
                              <span className="font-semibold text-slate-800">
                                {msg.structured_data.loan_eligibility.debt_to_income_ratio_pct}%
                              </span>
                            </div>
                          </div>

                          {/* Rule Checklist */}
                          {msg.structured_data.loan_eligibility.criteria_evaluation && (
                            <div className="space-y-1 text-xs">
                              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                                Criteria Checklist
                              </p>
                              {Object.entries(
                                msg.structured_data.loan_eligibility.criteria_evaluation
                              ).map(([criterion, passed]: any, i) => (
                                <div
                                  key={i}
                                  className="flex items-center gap-2 py-0.5 text-slate-700"
                                >
                                  {passed ? (
                                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                                  ) : (
                                    <XCircle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
                                  )}
                                  <span className={passed ? 'text-slate-800' : 'text-rose-700 font-medium'}>
                                    {criterion}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Mandatory explicit disclaimer */}
                          <div className="mt-3 p-2 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-900 flex items-start gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                            <span>
                              <strong>Demonstration Disclaimer:</strong> This calculation is an illustrative mock evaluation for TCS Technology Day and does not constitute a real credit approval or binding banking contract.
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Metadata Pill Bar below Assistant response */}
                {!isUser && (
                  <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 px-1">
                    {msg.tools_executed && msg.tools_executed.length > 0 && (
                      <div className="flex items-center gap-1 bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full font-mono">
                        <ShieldCheck className="w-3 h-3 text-blue-600" />
                        <span>Tools: {msg.tools_executed.map((t) => t.tool_name).join(', ')}</span>
                      </div>
                    )}
                    {msg.source && (
                      <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                        Engine: {msg.source}
                      </span>
                    )}
                    {msg.latency_ms !== undefined && (
                      <span className="flex items-center gap-0.5 text-slate-500">
                        <Clock className="w-2.5 h-2.5" /> {msg.latency_ms} ms
                      </span>
                    )}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 max-w-4xl mx-auto justify-start animate-in fade-in duration-200">
            <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-1">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-white border border-slate-200 text-sm rounded-tl-none shadow-xs flex items-center gap-3 text-slate-600">
              <span className="flex space-x-1.5">
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
              </span>
              <span className="text-xs font-medium text-slate-500">
                Executing verified banking query tools...
              </span>
            </div>
          </div>
        )}

        {/* Error Notification with Retry */}
        {errorMessage && (
          <div className="max-w-4xl mx-auto p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => handleSendMessage()}
              className="flex items-center gap-1 font-bold text-rose-700 hover:text-rose-900 px-2 py-1 rounded bg-rose-100 hover:bg-rose-200 transition"
            >
              <RotateCcw className="w-3 h-3" /> Retry
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Cards Carousel */}
      <div className="bg-slate-100/70 border-t border-slate-200/80 px-4 py-2.5 overflow-x-auto flex items-center gap-2 flex-shrink-0">
        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap pl-2">
          Suggestions:
        </span>
        {suggestedPrompts.map((s, idx) => {
          const Icon = s.icon;
          return (
            <button
              key={idx}
              onClick={() => handleSendMessage(s.prompt)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white hover:bg-blue-50 hover:border-blue-300 border border-slate-200 text-xs font-medium text-slate-700 hover:text-blue-800 transition shadow-2xs whitespace-nowrap group"
            >
              <Icon className="w-3 h-3 text-blue-600 group-hover:scale-110 transition-transform" />
              <span>{s.title}</span>
            </button>
          );
        })}
      </div>

      {/* Multiline Input & Send Footer */}
      <div className="bg-white border-t border-slate-200 p-4 flex-shrink-0 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-end gap-2 bg-slate-50 rounded-2xl border border-slate-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition p-2">
          <textarea
            ref={textareaRef}
            rows={1}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask any banking question (e.g., 'What is my current balance, and what did I spend on food?')..."
            className="flex-1 bg-transparent border-0 resize-none outline-none text-sm text-slate-900 placeholder:text-slate-400 max-h-32 py-1.5 px-2"
          />

          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || isLoading}
            className={`p-2.5 rounded-xl transition flex items-center justify-center flex-shrink-0 ${
              inputMessage.trim() && !isLoading
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-600/30'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
            title="Send query"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[11px] text-center text-slate-400 mt-2">
          Powered by NexaBank Tool-Calling Architecture • Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

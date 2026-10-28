import React, { useState } from 'react';
import {
  HelpCircle,
  Search,
  BookOpen,
  PhoneCall,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  FileText,
  CreditCard,
  Send
} from 'lucide-react';

const FAQS = [
  {
    q: 'How do I download my monthly account statement?',
    a: 'You can download monthly statements by going to "Transactions" and clicking "Export Statement (.CSV)" or visiting "My Accounts" to view account-specific activity. You can also ask NexaBank AI "Download my statement".',
    category: 'Statements',
  },
  {
    q: 'How can I block or reset my debit card PIN?',
    a: 'Go to Profile & Security > Card Controls. You can instantly freeze cards or generate a new secure PIN. Alternatively, type "Block my debit card" in the AI Assistant.',
    category: 'Cards',
  },
  {
    q: 'What documents are required for home loan tax benefit certificates?',
    a: 'Section 24 (interest deduction up to ₹2 Lakhs) and Section 80C (principal repayment up to ₹1.5 Lakhs) certificates are automatically pre-computed in "Loans & Rates".',
    category: 'Loans',
  },
  {
    q: 'What are the daily UPI and NEFT transfer limits?',
    a: 'NexaBank standard limits: UPI up to ₹1,00,000 per 24 hours; IMPS up to ₹5,00,000; NEFT/RTGS has no maximum ceiling for priority customers.',
    category: 'Transfers',
  },
  {
    q: 'How often is savings account interest calculated and credited?',
    a: 'Interest on all NexaBank Savings accounts is calculated daily on the end-of-day ledger balance and automatically credited on the final day of each calendar quarter.',
    category: 'Interest',
  },
];

export const HelpPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const filteredFaqs = FAQS.filter(
    (f) =>
      f.q.toLowerCase().includes(search.toLowerCase()) ||
      f.a.toLowerCase().includes(search.toLowerCase()) ||
      f.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-4xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Help & Support Knowledgebase</h2>
        <p className="text-xs text-slate-500">
          Frequently asked banking questions, guidelines, and customer assistance
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search topics (e.g. statement, card PIN, UPI limits, interest)..."
          className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 shadow-xs"
        />
      </div>

      {/* Accordion FAQs */}
      <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 shadow-xs overflow-hidden">
        {filteredFaqs.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="p-4 transition">
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full flex items-center justify-between text-left text-sm font-bold text-slate-900 gap-4"
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    {faq.category}
                  </span>
                  <span>{faq.q}</span>
                </div>
                {isOpen ? (
                  <ChevronUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                )}
              </button>

              {isOpen && (
                <div className="mt-3 pl-2 text-xs text-slate-600 leading-relaxed border-l-2 border-blue-500 pt-1">
                  {faq.a}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Support Contact Box */}
      <div className="p-6 rounded-2xl bg-slate-900 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg">
        <div className="space-y-1">
          <p className="font-bold text-sm">Need immediate concierge support?</p>
          <p className="text-xs text-slate-400">
            24/7 dedicated support desk for TCS Technology Day demonstration
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-slate-800 px-4 py-2 rounded-xl border border-slate-700 text-blue-400">
          <PhoneCall className="w-4 h-4 text-blue-400" />
          <span>1800-NEXA-BANK</span>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { ShieldAlert, Sparkles } from 'lucide-react';

interface DemoBadgeProps {
  compact?: boolean;
}

export const DemoBadge: React.FC<DemoBadgeProps> = ({ compact = false }) => {
  if (compact) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
        Demo Mode
      </span>
    );
  }

  return (
    <div className="bg-amber-50/90 border-b border-amber-200/80 px-4 py-1.5 text-xs text-amber-900 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-700 flex-shrink-0" />
        <span className="font-medium">
          <strong>NexaBank Demonstration Environment:</strong> All account balances, transactions, and credit decisions are synthetic data for TCS Technology Day.
        </span>
      </div>
      <div className="flex items-center gap-1.5 text-amber-800 font-semibold text-[11px] bg-amber-100/70 px-2 py-0.5 rounded border border-amber-200">
        <Sparkles className="w-3 h-3 text-amber-600" />
        Simulated Bank APIs Active
      </div>
    </div>
  );
};

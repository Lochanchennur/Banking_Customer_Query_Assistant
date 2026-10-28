import React, { useEffect, useState } from 'react';
import {
  Landmark,
  Calculator,
  Percent,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Info,
  Clock,
  Sparkles
} from 'lucide-react';
import { BankingProduct, Customer, LoanEligibilityResult } from '../types/banking';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface LoansPageProps {
  customer: Customer;
}

export const LoansPage: React.FC<LoansPageProps> = ({ customer }) => {
  const [products, setProducts] = useState<BankingProduct[]>([]);
  const [loading, setLoading] = useState(true);

  // Calculator Form State
  const [loanType, setLoanType] = useState('PERSONAL_LOAN');
  const [requestedAmount, setRequestedAmount] = useState(500000);
  const [tenureMonths, setTenureMonths] = useState(36);
  const [monthlyIncome, setMonthlyIncome] = useState(customer.monthly_income || 100000);
  const [existingEmis, setExistingEmis] = useState(0);

  const [calculating, setCalculating] = useState(false);
  const [calcResult, setCalcResult] = useState<LoanEligibilityResult | null>(null);

  useEffect(() => {
    loadProducts();
    // Run an initial indicative calculation
    runCalculation(500000, 36);
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const res = await api.getProducts();
      setProducts(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runCalculation = async (amt = requestedAmount, tenure = tenureMonths) => {
    try {
      setCalculating(true);
      const res = await api.checkLoanEligibility({
        product_type: loanType,
        requested_amount: amt,
        tenure_months: tenure,
        declared_monthly_income: monthlyIncome,
        declared_existing_emis: existingEmis,
      });
      setCalcResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setCalculating(false);
    }
  };

  const handleCalculateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runCalculation();
  };

  if (loading) return <LoadingSpinner message="Loading banking products & rate tables..." size="lg" />;

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Banking Products & Interest Rates</h2>
        <p className="text-xs text-slate-500">
          Transparent rates, loan parameters, and deterministic eligibility calculations
        </p>
      </div>

      {/* 1. Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {products.map((prod) => (
          <div
            key={prod.id}
            className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between space-y-4 hover:border-blue-400 hover:shadow-md transition"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  {prod.product_type.replace('_', ' ')}
                </span>
                <span className="text-[11px] font-semibold text-slate-500">{prod.rate_type}</span>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 text-base">{prod.name}</h3>
                <p className="text-xs text-slate-500 line-clamp-2 mt-1">{prod.headline}</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">
                  Configured Demo Rate
                </span>
                <p className="text-2xl font-extrabold text-blue-600 mt-0.5">
                  {prod.interest_rate}% <span className="text-xs text-slate-500 font-normal">p.a.</span>
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-600">
                <div className="flex justify-between">
                  <span className="text-slate-400">Limits:</span>
                  <span className="font-semibold text-slate-800">
                    ₹{(prod.min_amount / 1000).toFixed(0)}k - ₹{(prod.max_amount / 100000).toFixed(0)}L
                  </span>
                </div>
                {prod.max_tenure_months > 0 && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Tenure:</span>
                    <span className="font-semibold text-slate-800">
                      {prod.min_tenure_months} to {prod.max_tenure_months} mo
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-400">Fee:</span>
                  <span className="font-semibold text-slate-800">
                    {prod.processing_fee_pct > 0 ? `${prod.processing_fee_pct}%` : 'Nil'}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500">
              <p className="font-medium text-slate-700 mb-0.5">Eligibility Guideline:</p>
              <p className="line-clamp-2">{prod.eligibility_criteria_summary}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 2. Interactive Indicative Loan Eligibility Calculator */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-600/20">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Indicative Personal & Home Loan Eligibility Engine
              </h3>
              <p className="text-xs text-slate-500">
                Simulate mock lending decisions with deterministic DTI and credit rules
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            Deterministic Engine Active
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Calculator Inputs (5 cols) */}
          <form onSubmit={handleCalculateSubmit} className="lg:col-span-5 space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Select Product</label>
              <select
                value={loanType}
                onChange={(e) => setLoanType(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500"
              >
                <option value="PERSONAL_LOAN">NexaFlexi Personal Loan (10.75% p.a.)</option>
                <option value="HOME_LOAN">NexaDream Home Loan (8.40% p.a.)</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <label className="font-bold text-slate-700">Requested Principal Amount</label>
                <span className="font-extrabold text-blue-600">
                  ₹{requestedAmount.toLocaleString('en-IN')}
                </span>
              </div>
              <input
                type="range"
                min={50000}
                max={5000000}
                step={25000}
                value={requestedAmount}
                onChange={(e) => setRequestedAmount(Number(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>₹50,000</span>
                <span>₹50,00,000</span>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                Repayment Tenure (Months)
              </label>
              <div className="grid grid-cols-5 gap-2">
                {[12, 24, 36, 48, 60].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTenureMonths(t)}
                    className={`py-2 rounded-xl text-xs font-bold transition ${
                      tenureMonths === t
                        ? 'bg-blue-600 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {t}M
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                Declared Net Monthly Income (₹)
              </label>
              <input
                type="number"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(Number(e.target.value))}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-400">
                Pre-filled from your profile salary records
              </span>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                Existing Monthly EMIs / Obligations (₹)
              </label>
              <input
                type="number"
                value={existingEmis}
                onChange={(e) => setExistingEmis(Number(e.target.value))}
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={calculating}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition shadow-md shadow-blue-600/30 flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Evaluate Eligibility</span>
            </button>
          </form>

          {/* Results Card (7 cols) */}
          <div className="lg:col-span-7 bg-slate-50 rounded-2xl p-6 border border-slate-200 flex flex-col justify-between space-y-4">
            {calcResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Assessment Outcome
                    </span>
                    <h4 className="text-base font-extrabold text-slate-900 mt-0.5">
                      {calcResult.product_type.replace('_', ' ')}
                    </h4>
                  </div>
                  <span
                    className={`text-xs font-bold px-3 py-1 rounded-full ${
                      calcResult.eligible
                        ? calcResult.status === 'APPROVED'
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-amber-100 text-amber-800 border border-amber-200'
                        : 'bg-rose-100 text-rose-800 border border-rose-200'
                    }`}
                  >
                    {calcResult.status}
                  </span>
                </div>

                {/* Key Numbers Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white p-4 rounded-xl border border-slate-200">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Approved Limit
                    </span>
                    <span className="text-base font-extrabold text-slate-900 tabular-nums">
                      ₹{calcResult.approved_amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Estimated EMI
                    </span>
                    <span className="text-base font-extrabold text-blue-600 tabular-nums">
                      ₹{calcResult.estimated_emi.toLocaleString('en-IN')}/mo
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Interest Rate
                    </span>
                    <span className="text-base font-extrabold text-slate-800">
                      {calcResult.interest_rate}% p.a.
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      DTI Ratio
                    </span>
                    <span
                      className={`text-base font-extrabold ${
                        calcResult.debt_to_income_ratio_pct <= 50 ? 'text-emerald-600' : 'text-rose-600'
                      }`}
                    >
                      {calcResult.debt_to_income_ratio_pct}%
                    </span>
                  </div>
                </div>

                {/* Explanation */}
                <p className="text-xs text-slate-700 bg-white p-3 rounded-xl border border-slate-200 leading-relaxed">
                  {calcResult.reason}
                </p>

                {/* Criteria Checklist */}
                <div className="space-y-1.5 pt-2">
                  <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Rule Evaluation Checklist
                  </p>
                  {Object.entries(calcResult.criteria_evaluation).map(([rule, passed], i) => (
                    <div key={i} className="flex items-center gap-2 text-xs py-1">
                      {passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                      )}
                      <span className={passed ? 'text-slate-800' : 'text-rose-700 font-semibold'}>
                        {rule}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Mandatory Disclaimer */}
                <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-[11px] flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>Demonstration Disclaimer:</strong> {calcResult.disclaimer}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-400 text-xs">
                Select your parameters and click Evaluate Eligibility
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

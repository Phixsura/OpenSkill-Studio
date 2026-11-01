"use client";

interface EarningsSummary { gross: string; net: string; fee_pct: number; }
interface PayoutSummary { pending_cents: number; total_payouts: number; }
interface EarningsPageLayoutProps { summary: EarningsSummary; payouts: PayoutSummary; hasTaxInfo: boolean;
  onRequestPayout: () => void; onAddTaxInfo: () => void; children: React.ReactNode; }

export function EarningsPageLayout({ summary, payouts, hasTaxInfo, onRequestPayout, onAddTaxInfo, children }: EarningsPageLayoutProps) {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Earnings</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Gross Revenue</p>
          <p className="text-2xl font-bold">{summary.gross}</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Net Earnings ({100 - summary.fee_pct}%)</p>
          <p className="text-2xl font-bold text-green-600">{summary.net}</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Pending Payout</p>
          <p className="text-2xl font-bold">${(payouts.pending_cents / 100).toFixed(2)}</p>
          <button onClick={onRequestPayout} disabled={payouts.pending_cents < 5000}
            className="mt-2 rounded bg-green-600 px-3 py-1 text-xs text-white disabled:opacity-50">
            {payouts.pending_cents >= 5000 ? "Request Payout" : "Min $50 for payout"}
          </button>
        </div>
      </div>
      {!hasTaxInfo && (
        <div className="rounded bg-yellow-50 p-3 text-sm text-yellow-700 dark:bg-yellow-900/20">
          ⚠️ Tax information required for payouts.
          <button onClick={onAddTaxInfo} className="ml-2 underline">Add tax info</button>
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}

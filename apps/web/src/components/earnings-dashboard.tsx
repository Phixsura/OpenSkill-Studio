"use client";

interface EarningsDashboardProps { grossCents: number; netCents: number; feePct: number; balanceCents: number; payoutEligible: boolean; onRequestPayout: () => void; }

export function EarningsDashboard({ grossCents, netCents, feePct, balanceCents, payoutEligible, onRequestPayout }: EarningsDashboardProps) {
  const fmt = (c: number) => `$${(c / 100).toFixed(2)}`;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Earnings</h3>
      <div className="mt-3 grid grid-cols-3 gap-4 text-center">
        <div><p className="text-xl font-bold">{fmt(grossCents)}</p><p className="text-xs text-gray-400">Gross</p></div>
        <div><p className="text-xl font-bold text-green-600">{fmt(netCents)}</p><p className="text-xs text-gray-400">Net ({100 - feePct}%)</p></div>
        <div><p className="text-xl font-bold">{fmt(balanceCents)}</p><p className="text-xs text-gray-400">Balance</p></div>
      </div>
      <button onClick={onRequestPayout} disabled={!payoutEligible}
        className="mt-3 w-full rounded bg-green-600 py-2 text-sm text-white disabled:opacity-50">
        {payoutEligible ? "Request Payout" : `$${((5000 - balanceCents) / 100).toFixed(2)} until payout`}
      </button>
    </div>
  );
}

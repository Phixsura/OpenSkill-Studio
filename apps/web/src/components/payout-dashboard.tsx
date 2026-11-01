"use client";

interface Payout {
  id: string;
  grossCents: number;
  taxCents: number;
  netCents: number;
  status: "pending" | "processing" | "completed" | "failed" | "on_hold";
  paymentMethod: string;
  reference?: string;
  createdAt: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏳" },
  processing: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔄" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  on_hold: { color: "bg-gray-200 text-gray-600 dark:bg-gray-800", icon: "⏸" },
};

function fmt(cents: number) {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

export function PayoutDashboard({
  payouts,
  balanceCents,
  thresholdCents,
  onRequestPayout,
}: {
  payouts: Payout[];
  balanceCents: number;
  thresholdCents: number;
  onRequestPayout?: () => void;
}) {
  const totalPaid = payouts.filter((p) => p.status === "completed")
    .reduce((sum, p) => sum + p.netCents, 0);
  const canPayout = balanceCents >= thresholdCents;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">💸 Payouts</h2>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Balance</span>
          <span className="text-lg font-bold text-green-600">{fmt(balanceCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Threshold</span>
          <span className="text-lg font-bold">{fmt(thresholdCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Total Paid</span>
          <span className="text-lg font-bold text-blue-600">{fmt(totalPaid)}</span>
        </div>
      </div>

      <button onClick={onRequestPayout} disabled={!canPayout}
        className="w-full text-sm bg-green-600 text-white py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed">
        {canPayout ? "Request Payout" : `Need ${fmt(thresholdCents - balanceCents)} more`}
      </button>

      <div className="space-y-2">
        {payouts.map((p) => {
          const cfg = statusConfig[p.status];
          return (
            <div key={p.id} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-bold text-sm">{fmt(p.netCents)}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{p.status}</span>
                </div>
                <span className="text-xs text-gray-400">{p.paymentMethod}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Gross {fmt(p.grossCents)} · Tax {fmt(p.taxCents)} · {p.createdAt}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

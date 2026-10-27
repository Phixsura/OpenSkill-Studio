"use client";

interface BudgetSnapshot {
  app_id: string;
  slo_target_pct: number;
  actual_success_pct: number;
  budget_total_minutes: number;
  budget_consumed_minutes: number;
  budget_remaining_minutes: number;
  budget_remaining_pct: number;
  burn_rate: number;
  status: "healthy" | "warning" | "critical" | "exhausted";
  window_days: number;
}

interface ErrorBudgetCardProps {
  snapshot: BudgetSnapshot;
  appName: string;
}

const STATUS_STYLES: Record<string, { label: string; color: string; ring: string }> = {
  healthy: { label: "Healthy", color: "text-green-600", ring: "stroke-green-500" },
  warning: { label: "Warning", color: "text-yellow-600", ring: "stroke-yellow-500" },
  critical: { label: "Critical", color: "text-red-600", ring: "stroke-red-500" },
  exhausted: { label: "Exhausted", color: "text-red-700", ring: "stroke-red-600" },
};

function BudgetRing({ pct, status }: { pct: number; status: string }) {
  const r = 36;
  const c = 2 * Math.PI * r;
  const offset = c - (Math.max(0, pct) / 100) * c;
  const st = STATUS_STYLES[status] ?? STATUS_STYLES.exhausted;
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="88" height="88" className="-rotate-90">
        <circle
          cx="44"
          cy="44"
          r={r}
          fill="none"
          strokeWidth="6"
          className="stroke-gray-200 dark:stroke-gray-700"
        />
        <circle
          cx="44"
          cy="44"
          r={r}
          fill="none"
          strokeWidth="6"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={st.ring}
        />
      </svg>
      <div className="absolute text-center">
        <p className={`text-lg font-bold ${st.color}`}>{pct.toFixed(0)}%</p>
        <p className="text-[9px] text-gray-500">remaining</p>
      </div>
    </div>
  );
}

export function ErrorBudgetCard({ snapshot, appName }: ErrorBudgetCardProps) {
  const st = STATUS_STYLES[snapshot.status] ?? STATUS_STYLES.exhausted;
  const burnColor =
    snapshot.burn_rate > 1
      ? "text-red-600 font-bold"
      : snapshot.burn_rate > 0.5
        ? "text-yellow-600"
        : "text-green-600";

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Error Budget</h3>
          <p className="text-xs text-gray-500">
            {appName} • {snapshot.window_days}-day window
          </p>
        </div>
        <BudgetRing pct={snapshot.budget_remaining_pct} status={snapshot.status} />
      </div>

      {/* Status banner */}
      <div
        className={`px-4 py-2 text-xs font-medium ${st.color} ${snapshot.status === "exhausted" ? "bg-red-50 dark:bg-red-900/10" : snapshot.status === "critical" ? "bg-red-50 dark:bg-red-900/10" : ""}`}
      >
        {snapshot.status === "exhausted"
          ? "🚨 Error budget exhausted — SLO breached"
          : snapshot.status === "critical"
            ? "⚠️ Error budget critical — action needed"
            : snapshot.status === "warning"
              ? "⚡ Error budget declining"
              : "✓ Error budget healthy"}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-3 px-4 py-3">
        <div>
          <p className="text-[10px] text-gray-500">SLO Target</p>
          <p className="text-sm font-bold">{snapshot.slo_target_pct}%</p>
        </div>
        <div>
          <p className="text-[10px] text-gray-500">Actual Success</p>
          <p className="text-sm font-bold">{snapshot.actual_success_pct}%</p>
        </div>
        <div>
          <p className="text-[10px] text-gray-500">Budget Remaining</p>
          <p className="text-sm font-medium">{snapshot.budget_remaining_minutes.toFixed(0)} min</p>
        </div>
        <div>
          <p className="text-[10px] text-gray-500">Burn Rate</p>
          <p className={`text-sm font-medium ${burnColor}`}>{snapshot.burn_rate.toFixed(2)}×</p>
        </div>
      </div>
    </div>
  );
}

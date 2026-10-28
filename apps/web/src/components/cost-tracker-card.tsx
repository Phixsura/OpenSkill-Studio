"use client";

interface CostBreakdown {
  category: string;
  amount_cents: number;
}

interface CostTrackerCardProps {
  totalDollars: number;
  breakdown: CostBreakdown[];
  appName: string;
}

const CAT_COLORS: Record<string, string> = {
  compute: "bg-blue-500",
  storage: "bg-green-500",
  network: "bg-yellow-500",
  api_calls: "bg-purple-500",
};

export default function CostTrackerCard({
  totalDollars,
  breakdown,
  appName,
}: CostTrackerCardProps) {
  const totalCents = breakdown.reduce((s, b) => s + b.amount_cents, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Cost Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-lg font-bold text-gray-800 dark:text-gray-200">
          ${totalDollars.toFixed(2)}
        </span>
      </div>

      {/* Stacked bar */}
      {totalCents > 0 && (
        <div className="mb-3 flex h-3 overflow-hidden rounded-full">
          {breakdown.map((b) => {
            const pct = (b.amount_cents / totalCents) * 100;
            const color = CAT_COLORS[b.category] ?? "bg-gray-400";
            return <div key={b.category} className={color} style={{ width: `${pct}%` }} />;
          })}
        </div>
      )}

      {/* Legend */}
      {breakdown.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No costs recorded</p>
      ) : (
        <div className="space-y-1">
          {breakdown
            .sort((a, b) => b.amount_cents - a.amount_cents)
            .map((b) => {
              const color = CAT_COLORS[b.category] ?? "bg-gray-400";
              return (
                <div key={b.category} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded ${color}`} />
                    <span className="capitalize text-gray-700 dark:text-gray-300">
                      {b.category.replace(/_/g, " ")}
                    </span>
                  </div>
                  <span className="font-medium text-gray-800 dark:text-gray-200">
                    ${(b.amount_cents / 100).toFixed(2)}
                  </span>
                </div>
              );
            })}
        </div>
      )}
    </div>
  );
}

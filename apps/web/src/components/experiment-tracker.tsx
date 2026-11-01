"use client";

interface ExperimentResult { experiment: string; metric: string; control: number;
  variant: number; liftPct: number; significant: boolean; winner: string; }
interface ExperimentTrackerProps { results: ExperimentResult[]; }

const WINNER_COLORS: Record<string, string> = {
  variant: "text-green-600", control: "text-blue-600", inconclusive: "text-gray-400",
};

export function ExperimentTracker({ results }: ExperimentTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 Experiments</h3>
        <span className="text-xs text-gray-400">{results.length} experiments</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.experiment} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{r.experiment}</span>
              <span className={`text-xs font-medium ${WINNER_COLORS[r.winner] ?? ""}`}>{r.winner} {r.significant ? "✓" : ""}</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {r.metric}: {r.control} → {r.variant} ({r.liftPct > 0 ? "+" : ""}{r.liftPct}%)
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

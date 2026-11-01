"use client";

interface ModResult { textLength: number; action: string; flagCount: number; }
interface ContentModDashboardProps { total: number; approved: number; rejected: number;
  review: number; results: ModResult[]; }

const ACTION_BADGE: Record<string, { bg: string; label: string }> = {
  approve: { bg: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400", label: "Approved" },
  reject: { bg: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400", label: "Rejected" },
  review: { bg: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400", label: "Review" },
};

export function ContentModDashboard({ total, approved, rejected, review, results }: ContentModDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Content Moderation</h3>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Total", v: total }, { l: "Approved", v: approved },
          { l: "Rejected", v: rejected }, { l: "Review", v: review }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.slice(0, 10).map((r, i) => {
          const badge = ACTION_BADGE[r.action] ?? ACTION_BADGE.review;
          return (
            <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
              <span className="text-gray-400">{r.textLength} chars · {r.flagCount} flags</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${badge.bg}`}>{badge.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

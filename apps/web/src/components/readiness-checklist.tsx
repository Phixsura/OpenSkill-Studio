"use client";

interface ReadinessCheck { item: string; category: string; critical: boolean; ready: boolean; }
interface ReadinessChecklistProps { checks: ReadinessCheck[]; launchReady: boolean;
  readinessPct: number; criticalPass: number; criticalTotal: number; }

export function ReadinessChecklist({ checks, launchReady, readinessPct, criticalPass, criticalTotal }: ReadinessChecklistProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${launchReady ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold">🚀 Launch Readiness</h3>
        <div className="flex gap-2 text-xs">
          <span className={launchReady ? "text-green-600" : "text-red-500"}>
            {launchReady ? "✅ Ready to Launch" : "🚫 Not Ready"}
          </span>
          <span className="text-gray-400">{readinessPct}% · {criticalPass}/{criticalTotal} critical</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.item} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.ready ? "✅" : "❌"}</span>
              <span className="font-medium">{c.item}</span>
              {c.critical && <span className="text-red-400 text-[10px]">critical</span>}
            </div>
            <span className="text-gray-400">{c.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

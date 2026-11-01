"use client";

interface Quickstart { id: string; title: string; timeMin: number; category: string; completed: boolean; }
interface DevPortalHomeProps { quickstarts: Quickstart[]; progressPct: number;
  remainingTimeMin: number; developers: number; appsPublished: number; displayCalls: string; }

export function DevPortalHome({ quickstarts, progressPct, remainingTimeMin, developers, appsPublished, displayCalls }: DevPortalHomeProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10">
        <h2 className="text-xl font-bold">🚀 Developer Portal</h2>
        <div className="flex justify-center gap-6 mt-3 text-sm">
          <div><span className="font-bold">{developers.toLocaleString()}</span> <span className="text-gray-400">developers</span></div>
          <div><span className="font-bold">{appsPublished}</span> <span className="text-gray-400">apps</span></div>
          <div><span className="font-bold">{displayCalls}</span> <span className="text-gray-400">API calls</span></div>
        </div>
      </div>
      <div className="p-3 border-b dark:border-gray-700">
        <div className="flex justify-between text-xs mb-1">
          <span>Quick Starts</span>
          <span>{progressPct}% · {remainingTimeMin}min remaining</span>
        </div>
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {quickstarts.map(q => (
          <div key={q.id} className={`flex items-center justify-between px-4 py-2 ${q.completed ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span>{q.completed ? "✅" : "📘"}</span>
              <span className="text-sm">{q.title}</span>
            </div>
            <span className="text-xs text-gray-400">{q.timeMin}min</span>
          </div>
        ))}
      </div>
    </div>
  );
}

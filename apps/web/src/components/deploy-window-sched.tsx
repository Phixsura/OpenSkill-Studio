"use client";

interface DeployWindowSchedProps { currentWindow: string | null; allowed: boolean;
  currentHour: number; windows: { name: string; startHour: number; endHour: number }[]; }

export function DeployWindowSched({ currentWindow, allowed, currentHour, windows }: DeployWindowSchedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕐 Deploy Windows</h3>
        <span className={`text-xs ${allowed ? "text-green-600" : "text-red-500"}`}>
          {allowed ? `✅ ${currentWindow} — Deploy OK` : "🚫 Outside Window"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {windows.map(w => (
          <div key={w.name} className={`flex justify-between px-4 py-2 text-xs ${w.name === currentWindow ? "bg-green-50 dark:bg-green-900/10" : ""}`}>
            <span className="capitalize">{w.name.replaceAll("_", " ")}</span>
            <span className="text-gray-400">{w.startHour}:00 — {w.endHour}:00</span>
          </div>
        ))}
      </div>
    </div>
  );
}

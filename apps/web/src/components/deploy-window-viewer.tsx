"use client";

interface Window { name: string; dayOfWeek: number; startHour: number; durationHours: number; }
interface DeployWindowViewerProps { windows: Window[]; currentlyInWindow: boolean; nextWindowHours: number; }

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function DeployWindowViewer({ windows, currentlyInWindow, nextWindowHours }: DeployWindowViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗓️ Deploy Windows</h3>
        <span className={`text-xs font-bold ${currentlyInWindow ? "text-green-600" : "text-gray-400"}`}>
          {currentlyInWindow ? "✅ Window open" : `Next in ${nextWindowHours}h`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {windows.map(w => (
          <div key={w.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-semibold">{w.name}</span>
            <span className="text-gray-400">{DAYS[w.dayOfWeek]} {w.startHour}:00 — {(w.startHour + w.durationHours) % 24}:00 ({w.durationHours}h)</span>
          </div>
        ))}
      </div>
    </div>
  );
}

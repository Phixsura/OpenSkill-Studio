"use client";
interface LogFormatPanelProps { total: number; byLevel: Record<string, number>; byService: Record<string, number>; }
const LEVEL_COLOR: Record<string, string> = { INFO: "text-blue-500", ERROR: "text-red-500", WARN: "text-yellow-600", DEBUG: "text-gray-400" };
export function LogFormatPanel({ total, byLevel, byService }: LogFormatPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Log Analytics</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} logs</span>
      </div>
      <div className="grid grid-cols-2 gap-4 p-4 text-xs">
        <div>
          <div className="text-gray-400 mb-1 font-semibold">By Level</div>
          {Object.entries(byLevel).map(([l, c]) => (
            <div key={l} className="flex justify-between"><span className={LEVEL_COLOR[l] ?? ""}>{l}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
        <div>
          <div className="text-gray-400 mb-1 font-semibold">By Service</div>
          {Object.entries(byService).map(([s, c]) => (
            <div key={s} className="flex justify-between"><span>{s}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
      </div>
    </div>
  );
}

"use client";

interface ConsoleEntry { level: string; message: string; source: string; }
interface DebugConsolePanelProps { output: ConsoleEntry[]; total: number;
  byLevel: Record<string, number>; breakpoints: number; onClear: () => void; }

const LEVEL_STYLES: Record<string, string> = {
  info: "text-blue-400", warn: "text-yellow-400", error: "text-red-400",
  debug: "text-gray-500", log: "text-gray-300",
};

export function DebugConsolePanel({ output, total, byLevel, breakpoints, onClear }: DebugConsolePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-3 border-b dark:border-gray-700 bg-gray-900">
        <h3 className="text-sm font-semibold text-gray-200">🐛 Debug Console</h3>
        <div className="flex gap-2">
          <span className="text-[10px] text-gray-400">{total} logs · {breakpoints} bp</span>
          <button onClick={onClear} className="text-[10px] text-red-400 hover:underline">Clear</button>
        </div>
      </div>
      <div className="bg-gray-950 text-gray-200 font-mono text-xs max-h-48 overflow-y-auto p-2">
        {output.map((e, i) => (
          <div key={i} className="py-0.5">
            <span className={`${LEVEL_STYLES[e.level] ?? ""} uppercase mr-1`}>[{e.level}]</span>
            {e.source && <span className="text-gray-500 mr-1">{e.source}:</span>}
            <span>{e.message}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-2 px-3 py-1.5 bg-gray-900 border-t border-gray-800 text-[10px]">
        {Object.entries(byLevel).map(([lv, c]) => (
          <span key={lv} className={LEVEL_STYLES[lv] ?? "text-gray-400"}>{lv}: {c}</span>
        ))}
      </div>
    </div>
  );
}

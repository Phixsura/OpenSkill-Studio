"use client";
interface BreakingChange { type: string; field: string; }
interface CompatCheckPanelProps { compatible: boolean; breaking: BreakingChange[];
  warnings: number; fromVersion: string; toVersion: string; }
export function CompatCheckPanel({ compatible, breaking, warnings, fromVersion, toVersion }: CompatCheckPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 API Compatibility</h3>
        <span className={`text-xs font-bold ${compatible ? "text-green-600" : "text-red-500"}`}>
          {fromVersion} → {toVersion}: {compatible ? "✅ Compatible" : `❌ ${breaking.length} breaking`}
        </span>
      </div>
      {breaking.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {breaking.map((b, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{b.field}</span>: {b.type.replace("_", " ")}
            </div>
          ))}
        </div>
      )}
      {warnings > 0 && <div className="px-4 py-2 text-xs text-yellow-600">{warnings} warning(s)</div>}
    </div>
  );
}

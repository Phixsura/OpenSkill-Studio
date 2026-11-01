"use client";

interface ConfigError { field: string; error: string; severity: string; }
interface ConfigValidPanelProps { valid: boolean; errors: ConfigError[]; fieldsChecked: number; }

export function ConfigValidPanel({ valid, errors, fieldsChecked }: ConfigValidPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Config Validator</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} issues`} · {fieldsChecked} fields
        </span>
      </div>
      {errors.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
              <div><span className="font-mono">{e.field}</span>: <span className="text-gray-400">{e.error}</span></div>
              <span className={e.severity === "error" ? "text-red-500" : "text-yellow-600"}>{e.severity}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">All fields valid</div>
      )}
    </div>
  );
}

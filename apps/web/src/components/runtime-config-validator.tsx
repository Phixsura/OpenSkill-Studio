"use client";

interface ConfigError { key: string; error: string; }
interface ConfigWarning { key: string; warning: string; }
interface RuntimeConfigValidatorProps { valid: boolean; errors: ConfigError[];
  warnings: ConfigWarning[]; checked: number; }

export function RuntimeConfigValidator({ valid, errors, warnings, checked }: RuntimeConfigValidatorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${valid ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">{valid ? "✅" : "❌"} Runtime Config</h3>
        <span className="text-xs text-gray-400">{checked} keys checked</span>
      </div>
      {errors.length > 0 && (
        <div className="border-b dark:border-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="flex gap-2 px-4 py-1.5 text-xs">
              <span className="text-red-500">●</span>
              <span className="font-mono">{e.key}</span>
              <span className="text-gray-400">{e.error.replaceAll("_", " ")}</span>
            </div>
          ))}
        </div>
      )}
      {warnings.length > 0 && warnings.map((w, i) => (
        <div key={i} className="flex gap-2 px-4 py-1.5 text-xs">
          <span className="text-yellow-500">●</span>
          <span className="font-mono">{w.key}</span>
          <span className="text-gray-400">{w.warning.replaceAll("_", " ")}</span>
        </div>
      ))}
    </div>
  );
}

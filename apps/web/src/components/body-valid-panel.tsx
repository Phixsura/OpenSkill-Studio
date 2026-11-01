"use client";

interface BodyError { field: string; error: string; }
interface BodyValidPanelProps { valid: boolean; errors: BodyError[]; endpoint: string; }

export function BodyValidPanel({ valid, errors, endpoint }: BodyValidPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Body Validation</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} errors`} · {endpoint}
        </span>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{e.field}</span>: {e.error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";
interface HeaderError { header: string; error: string; }
interface HeaderValidPanelProps { valid: boolean; errors: HeaderError[]; headersChecked: number; totalSizeBytes: number; }
export function HeaderValidPanel({ valid, errors, headersChecked, totalSizeBytes }: HeaderValidPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Header Validation</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} errors`} · {headersChecked} headers · {totalSizeBytes}B
        </span>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{e.header}</span>: {e.error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";
interface RequestIdPanelProps { requestId: string; prefix: string; traceable: boolean; valid: boolean; }
export function RequestIdPanel({ requestId, prefix, traceable, valid }: RequestIdPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🆔 Request ID</h3>
        <span className={`text-xs ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : "❌ Invalid"} · prefix: {prefix}
        </span>
      </div>
      <div className="p-4 text-xs">
        <div className="font-mono bg-gray-50 dark:bg-gray-900 p-2 rounded break-all">{requestId}</div>
        <div className="text-gray-400 mt-1">{traceable ? "📍 Timestamp embedded" : "🔀 Random only"}</div>
      </div>
    </div>
  );
}

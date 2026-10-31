"use client";

interface Interceptor {
  interceptorId: string;
  name: string;
  phase: "before" | "after";
  action: "pass" | "modify" | "block" | "cache" | "delay";
  enabled: boolean;
  executionCount: number;
  order: number;
}

const actionConfig: Record<string, { color: string; icon: string }> = {
  pass: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "➡️" },
  modify: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "✏️" },
  block: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🚫" },
  cache: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "💾" },
  delay: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏱️" },
};

export function RequestInterceptorPanel({
  interceptors,
  onToggle,
  onRemove,
}: {
  interceptors: Interceptor[];
  onToggle?: (id: string) => void;
  onRemove?: (id: string) => void;
}) {
  const before = interceptors.filter((i) => i.phase === "before");
  const after = interceptors.filter((i) => i.phase === "after");

  const renderList = (items: Interceptor[], label: string) => (
    <div>
      <span className="text-xs font-semibold text-gray-500 uppercase">{label}</span>
      <div className="mt-1 space-y-1">
        {items.map((i) => {
          const cfg = actionConfig[i.action];
          return (
            <div key={i.interceptorId} className={`rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between ${!i.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 w-5">#{i.order}</span>
                <span>{cfg.icon}</span>
                <span className="text-sm font-medium">{i.name}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${cfg.color}`}>{i.action}</span>
                <span className="text-xs text-gray-400">×{i.executionCount}</span>
              </div>
              <div className="flex gap-1">
                <button onClick={() => onToggle?.(i.interceptorId)}
                  className={`text-xs px-2 py-0.5 rounded ${i.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {i.enabled ? "On" : "Off"}
                </button>
                <button onClick={() => onRemove?.(i.interceptorId)} className="text-xs text-red-500">✕</button>
              </div>
            </div>
          );
        })}
        {items.length === 0 && <span className="text-xs text-gray-400">No interceptors</span>}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔌 Request Interceptors</h2>
      {renderList(before, "Before Request")}
      {renderList(after, "After Response")}
    </div>
  );
}

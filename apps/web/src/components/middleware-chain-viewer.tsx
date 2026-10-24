"use client";

interface Middleware { order: number; name: string; type: string; enabled: boolean; }
interface MiddlewareChainViewerProps { chain: Middleware[]; enabled: number; total: number; }

const TYPE_ICONS: Record<string, string> = {
  transform: "🔄", auth: "🔐", rate_limit: "⏱️", cache: "💨", log: "📋",
};

export function MiddlewareChainViewer({ chain, enabled, total }: MiddlewareChainViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⛓️ Middleware Chain</h3>
        <span className="text-xs text-gray-400">{enabled}/{total} enabled</span>
      </div>
      <div className="flex items-center gap-1 p-4 flex-wrap">
        {chain.map((m, i) => (
          <div key={m.order} className="flex items-center">
            <div className={`px-3 py-2 rounded-lg text-xs text-center border ${m.enabled ? "border-green-300 dark:border-green-800" : "border-gray-300 dark:border-gray-600 opacity-50"}`}>
              <div>{TYPE_ICONS[m.type] ?? "⚙️"}</div>
              <div className="font-medium">{m.name}</div>
              <div className="text-[10px] text-gray-400">{m.type}</div>
            </div>
            {i < chain.length - 1 && <span className="text-gray-300 mx-1">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

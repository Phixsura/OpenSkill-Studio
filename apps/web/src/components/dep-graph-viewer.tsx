"use client";

interface DepNode { extensionId: string; version: string; deps: string[]; status: "resolved" | "missing" | "circular"; }

const statusStyle: Record<string, { border: string; bg: string; icon: string }> = {
  resolved: { border: "border-green-300 dark:border-green-700", bg: "bg-green-50 dark:bg-green-900/10", icon: "✅" },
  missing: { border: "border-red-300 dark:border-red-700", bg: "bg-red-50 dark:bg-red-900/10", icon: "❌" },
  circular: { border: "border-yellow-300 dark:border-yellow-700", bg: "bg-yellow-50 dark:bg-yellow-900/10", icon: "🔄" },
};

export function DepGraphViewer({ nodes }: { nodes: DepNode[] }) {
  if (!nodes.length) return <div className="text-center text-gray-400 py-6 text-sm">No dependencies</div>;
  return (
    <div className="space-y-2">
      {nodes.map((n, i) => {
        const s = statusStyle[n.status] || statusStyle.resolved;
        return (
          <div key={n.extensionId} className={`border ${s.border} ${s.bg} rounded-xl p-3`}>
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-xs w-5">{i + 1}.</span>
              <span>{s.icon}</span>
              <span className="font-medium text-sm">{n.extensionId}</span>
              <span className="text-xs text-gray-500">v{n.version}</span>
            </div>
            {n.deps.length > 0 && (
              <div className="ml-8 mt-1 flex gap-1 flex-wrap">
                {n.deps.map(d => <span key={d} className="text-xs bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded">→ {d}</span>)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

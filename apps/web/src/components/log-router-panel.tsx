"use client";

interface LogDestination {
  destId: string;
  name: string;
  destType: "console" | "webhook" | "aggregator" | "file";
  minLevel: string;
  enabled: boolean;
  routedCount: number;
}

const typeIcons: Record<string, string> = {
  console: "🖥️", webhook: "🔗", aggregator: "📊", file: "📄",
};

const levelColors: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-600",
  warn: "text-yellow-600", error: "text-red-600", fatal: "text-red-800",
};

export function LogRouterPanel({
  destinations,
  onToggle,
  onRemove,
}: {
  destinations: LogDestination[];
  onToggle?: (destId: string) => void;
  onRemove?: (destId: string) => void;
}) {
  const active = destinations.filter((d) => d.enabled).length;
  const totalRouted = destinations.reduce((s, d) => s + d.routedCount, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 Log Router</h2>
        <span className="text-sm text-gray-500">{active} active · {totalRouted.toLocaleString()} routed</span>
      </div>

      <div className="space-y-1">
        {destinations.map((dest) => (
          <div key={dest.destId} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between ${!dest.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span>{typeIcons[dest.destType]}</span>
              <span className="font-semibold text-sm">{dest.name}</span>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{dest.destType}</span>
              <span className={`text-xs ${levelColors[dest.minLevel] || ""}`}>≥{dest.minLevel}</span>
              <span className="text-xs text-gray-400">×{dest.routedCount}</span>
            </div>
            <div className="flex gap-1">
              <button onClick={() => onToggle?.(dest.destId)}
                className={`text-xs px-2 py-0.5 rounded ${dest.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                {dest.enabled ? "On" : "Off"}
              </button>
              <button onClick={() => onRemove?.(dest.destId)} className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

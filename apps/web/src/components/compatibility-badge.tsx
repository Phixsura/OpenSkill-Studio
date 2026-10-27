"use client";

interface CompatInfo { extensionVersion: string; platformVersion: string; status: string; }

const statusConfig: Record<string, { bg: string; icon: string; label: string }> = {
  compatible: { bg: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400", icon: "✅", label: "Compatible" },
  incompatible: { bg: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400", icon: "❌", label: "Incompatible" },
  untested: { bg: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400", icon: "❓", label: "Untested" },
  deprecated: { bg: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400", icon: "⚠️", label: "Deprecated" },
};

export function CompatibilityBadge({ compat }: { compat: CompatInfo }) {
  const cfg = statusConfig[compat.status] || statusConfig.untested;
  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${cfg.bg}`}>
      {cfg.icon} {cfg.label} · v{compat.extensionVersion} on v{compat.platformVersion}
    </span>
  );
}

export function CompatibilityMatrix({ entries }: { entries: CompatInfo[] }) {
  if (!entries.length) return <div className="text-center text-gray-400 py-4 text-sm">No compatibility data</div>;
  const platforms = [...new Set(entries.map(e => e.platformVersion))].sort();
  const versions = [...new Set(entries.map(e => e.extensionVersion))].sort();
  const lookup = new Map(entries.map(e => [`${e.extensionVersion}:${e.platformVersion}`, e.status]));

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr><th className="p-1.5 text-left">Ext ↓ / Platform →</th>
            {platforms.map(p => <th key={p} className="p-1.5">v{p}</th>)}
          </tr>
        </thead>
        <tbody>
          {versions.map(v => (
            <tr key={v}>
              <td className="p-1.5 font-mono">v{v}</td>
              {platforms.map(p => {
                const s = lookup.get(`${v}:${p}`) || "untested";
                const cfg = statusConfig[s] || statusConfig.untested;
                return <td key={p} className="p-1.5 text-center">{cfg.icon}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

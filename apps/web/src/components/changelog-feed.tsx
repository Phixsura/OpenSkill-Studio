"use client";

interface ChangelogEntry {
  entryId: string; extensionId: string; version: string;
  changes: string[]; changeType: string; publishedAt: number;
}

const typeConfig: Record<string, { icon: string; badge: string }> = {
  feature: { icon: "✨", badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400" },
  fix: { icon: "🐛", badge: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400" },
  breaking: { icon: "💥", badge: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400" },
  deprecation: { icon: "⚠️", badge: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400" },
};

export function ChangelogFeed({ entries }: { entries: ChangelogEntry[] }) {
  if (!entries.length) return <div className="text-center text-gray-400 py-6 text-sm">No changelog entries yet</div>;
  return (
    <div className="space-y-3">
      {entries.map((e) => {
        const cfg = typeConfig[e.changeType] || typeConfig.feature;
        return (
          <div key={e.entryId} className="border dark:border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <span>{cfg.icon}</span>
              <span className="font-bold text-sm">{e.extensionId}</span>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">v{e.version}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.badge}`}>{e.changeType}</span>
            </div>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-0.5 ml-6">
              {e.changes.map((c, i) => <li key={i}>• {c}</li>)}
            </ul>
          </div>
        );
      })}
    </div>
  );
}

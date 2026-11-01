"use client";

interface ApiChange { changeType: string; path: string; method: string; description: string; breaking: boolean; }
interface Changelog { fromVersion: string; toVersion: string; changes: ApiChange[]; }

const typeIcons: Record<string, string> = { added: "🟢", removed: "🔴", modified: "🟡", deprecated: "⚠️" };
const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600", PATCH: "text-purple-600" };

export function ApiChangelogViewer({ changelog }: { changelog: Changelog }) {
  const grouped = changelog.changes.reduce((acc, c) => {
    (acc[c.changeType] = acc[c.changeType] || []).push(c);
    return acc;
  }, {} as Record<string, ApiChange[]>);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="font-bold text-sm">API Changes</span>
        <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">{changelog.fromVersion} → {changelog.toVersion}</span>
        {changelog.changes.some(c => c.breaking) && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">Breaking</span>}
      </div>
      {Object.entries(grouped).map(([type, changes]) => (
        <div key={type}>
          <h4 className="text-xs font-semibold uppercase text-gray-500 mb-1">{typeIcons[type]} {type}</h4>
          <div className="space-y-1">
            {changes.map((c, i) => (
              <div key={i} className="flex items-center gap-2 text-sm border dark:border-gray-700 rounded-lg p-2">
                <span className={`font-mono text-xs font-bold ${methodColors[c.method] || ""}`}>{c.method}</span>
                <span className="font-mono text-xs">{c.path}</span>
                {c.breaking && <span className="text-xs text-red-500">💥</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
      {changelog.changes.length === 0 && <div className="text-center text-gray-400 text-sm py-4">No API changes</div>}
    </div>
  );
}

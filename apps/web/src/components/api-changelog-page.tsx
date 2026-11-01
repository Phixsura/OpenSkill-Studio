"use client";

interface Change { type: string; endpoint: string; description: string; }
interface ApiVersion { version: string; title: string; changeCount: number; }
interface ApiChangelogPageProps { versions: ApiVersion[]; selectedChanges: Change[] | null;
  selectedVersion: string | null; hasBreaking: boolean;
  onSelectVersion: (version: string) => void; }

const typeIcons: Record<string, string> = {
  added: "✨", changed: "🔄", deprecated: "⚠️", removed: "🗑️",
};
const typeBg: Record<string, string> = {
  added: "bg-green-100 text-green-700 dark:bg-green-900/30",
  changed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  deprecated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  removed: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function ApiChangelogPage({ versions, selectedChanges, selectedVersion, hasBreaking, onSelectVersion }: ApiChangelogPageProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">API Changelog</h2>
      <div className="flex gap-2">
        {versions.map(v => (
          <button key={v.version} onClick={() => onSelectVersion(v.version)}
            className={`rounded px-3 py-1 text-xs ${selectedVersion === v.version ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {v.title} ({v.changeCount})
          </button>
        ))}
      </div>
      {hasBreaking && <p className="text-xs text-red-600">⚠ Contains breaking changes</p>}
      {selectedChanges && (
        <div className="space-y-2">
          {selectedChanges.map((c, i) => (
            <div key={i} className="rounded-lg border p-3 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-xs ${typeBg[c.type] ?? ""}`}>{typeIcons[c.type] ?? "📌"} {c.type}</span>
                <code className="text-sm font-mono">{c.endpoint}</code>
              </div>
              <p className="mt-1 text-xs text-gray-500">{c.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

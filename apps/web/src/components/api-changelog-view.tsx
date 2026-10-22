"use client";

interface Change { type: string; description: string; }
interface ApiVersion { version: string; date: string; changes: Change[]; }

interface ApiChangelogViewProps { versions: ApiVersion[]; }

const TYPE_ICONS: Record<string, string> = { added: "✨", changed: "🔄", deprecated: "⚠️", removed: "🗑️", fixed: "🐛" };

export function ApiChangelogView({ versions }: ApiChangelogViewProps) {
  return (
    <div className="space-y-6">
      {versions.map(v => (
        <div key={v.version} className="border-l-2 border-blue-500 pl-4">
          <h3 className="font-semibold">API {v.version} <span className="text-xs text-gray-500">({v.date})</span></h3>
          <ul className="mt-2 space-y-1">{v.changes.map((c, i) => (
            <li key={i} className="text-sm">{TYPE_ICONS[c.type] ?? "•"} {c.description}</li>
          ))}</ul>
        </div>
      ))}
    </div>
  );
}

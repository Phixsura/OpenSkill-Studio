"use client";

interface Change { type: string; description: string; }

interface ReleaseNotesCardProps {
  version: string;
  date: string;
  changes: Change[];
  breaking?: boolean;
}

const TYPE_ICONS: Record<string, string> = {
  added: "✨", changed: "🔄", fixed: "🐛", removed: "🗑️", security: "🔒",
};

export function ReleaseNotesCard({ version, date, changes, breaking }: ReleaseNotesCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <h4 className="font-semibold">v{version}</h4>
        {breaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800">Breaking</span>}
        <span className="ml-auto text-xs text-gray-400">{date}</span>
      </div>
      {changes.length === 0 ? (
        <p className="text-sm text-gray-400">No changes listed</p>
      ) : (
        <ul className="space-y-1">
          {changes.map((c, i) => (
            <li key={i} className="text-sm">
              {TYPE_ICONS[c.type] ?? "•"} {c.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

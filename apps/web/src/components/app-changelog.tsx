"use client";

interface ChangelogEntry {
  version: string;
  notes: string;
  breaking: boolean;
  changes: Array<{
    type: string;
    items?: string[];
    breaking?: boolean;
  }>;
}

interface AppChangelogProps {
  entries: ChangelogEntry[];
}

const CHANGE_ICONS: Record<string, string> = {
  permissions_added: "🔑",
  permissions_removed: "🔓",
  events_added: "🔔",
  secrets_added: "🔐",
  ui_extensions_added: "🧩",
  sandbox_changed: "⚙️",
  config_schema_changed: "📋",
};

function formatChangeType(type: string): string {
  return type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function AppChangelog({ entries }: AppChangelogProps) {
  if (entries.length === 0) {
    return <p className="py-4 text-center text-sm text-gray-400">No changelog entries</p>;
  }

  return (
    <div className="space-y-6">
      {entries.map((entry) => (
        <div key={entry.version} className="border-l-2 border-gray-200 pl-4 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">{entry.version}</h3>
            {entry.breaking && (
              <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                Breaking
              </span>
            )}
          </div>
          {entry.notes && (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{entry.notes}</p>
          )}
          {entry.changes.length > 0 && (
            <ul className="mt-2 space-y-1">
              {entry.changes.map((change, i) => (
                <li key={i} className="text-sm">
                  <span className="mr-1">{CHANGE_ICONS[change.type] ?? "•"}</span>
                  <span className="font-medium">{formatChangeType(change.type)}</span>
                  {change.items && (
                    <span className="ml-1 text-gray-500">: {change.items.join(", ")}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

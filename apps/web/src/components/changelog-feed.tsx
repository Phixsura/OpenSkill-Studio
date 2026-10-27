"use client";

interface ChangeItem {
  category: "added" | "changed" | "fixed" | "removed" | "security" | "deprecated";
  description: string;
  breaking: boolean;
}

interface ChangelogEntry {
  version: string;
  title: string;
  items: ChangeItem[];
  published_at: string;
  has_breaking: boolean;
}

interface ChangelogFeedProps {
  appName: string;
  entries: ChangelogEntry[];
}

const CAT_STYLES: Record<string, { label: string; color: string; icon: string }> = {
  added: {
    label: "Added",
    color: "text-green-700 bg-green-100 dark:bg-green-900/20 dark:text-green-300",
    icon: "+",
  },
  changed: {
    label: "Changed",
    color: "text-blue-700 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300",
    icon: "~",
  },
  fixed: {
    label: "Fixed",
    color: "text-yellow-700 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-300",
    icon: "🔧",
  },
  removed: {
    label: "Removed",
    color: "text-red-700 bg-red-100 dark:bg-red-900/20 dark:text-red-300",
    icon: "−",
  },
  security: {
    label: "Security",
    color: "text-purple-700 bg-purple-100 dark:bg-purple-900/20 dark:text-purple-300",
    icon: "🔒",
  },
  deprecated: {
    label: "Deprecated",
    color: "text-orange-700 bg-orange-100 dark:bg-orange-900/20 dark:text-orange-300",
    icon: "⚠",
  },
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return iso;
  }
}

function EntryCard({ entry }: { entry: ChangelogEntry }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-bold dark:bg-gray-800">
            {entry.version}
          </code>
          <span className="text-sm font-medium">{entry.title}</span>
          {entry.has_breaking && (
            <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-bold text-red-700 dark:bg-red-900/20 dark:text-red-300">
              BREAKING
            </span>
          )}
        </div>
        <span className="text-xs text-gray-400">{formatDate(entry.published_at)}</span>
      </div>

      <div className="mt-2 space-y-1">
        {entry.items.map((item, i) => {
          const cat = CAT_STYLES[item.category] ?? CAT_STYLES.changed;
          return (
            <div key={i} className="flex items-start gap-2 text-xs">
              <span className={`shrink-0 rounded px-1 py-0.5 text-[9px] font-bold ${cat.color}`}>
                {cat.icon} {cat.label}
              </span>
              <span className={item.breaking ? "font-medium" : ""}>
                {item.breaking && <span className="text-red-600">⚠️ </span>}
                {item.description}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function ChangelogFeed({ appName, entries }: ChangelogFeedProps) {
  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold">Changelog</h2>
        <p className="text-xs text-gray-500">
          {appName} • {entries.length} releases
        </p>
      </div>

      {entries.length === 0 ? (
        <div className="rounded-lg border border-gray-200 py-8 text-center dark:border-gray-700">
          <span className="text-3xl">📝</span>
          <p className="mt-2 text-sm text-gray-500">No changelog entries yet</p>
        </div>
      ) : (
        entries.map((e) => <EntryCard key={e.version} entry={e} />)
      )}
    </div>
  );
}

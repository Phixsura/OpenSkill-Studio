"use client";

interface ChangeEntry {
  description: string;
  category: "added" | "changed" | "fixed" | "removed" | "security" | "deprecated";
  breaking: boolean;
}

interface ReleaseInfo {
  version: string;
  date: string;
  summary: string;
  entries: ChangeEntry[];
}

interface ChangelogCardProps {
  releases: ReleaseInfo[];
  appName: string;
}

const CATEGORY_STYLES: Record<string, { label: string; bg: string; text: string }> = {
  added: {
    label: "Added",
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
  },
  changed: {
    label: "Changed",
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
  },
  fixed: {
    label: "Fixed",
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
  },
  removed: {
    label: "Removed",
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
  },
  security: {
    label: "Security",
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
  },
  deprecated: {
    label: "Deprecated",
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-600 dark:text-gray-400",
  },
};

function CategoryBadge({ category }: { category: string }) {
  const st = CATEGORY_STYLES[category] ?? CATEGORY_STYLES.changed;
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}>
      {st.label}
    </span>
  );
}

function ReleaseSection({ release }: { release: ReleaseInfo }) {
  const hasBreaking = release.entries.some((e) => e.breaking);

  return (
    <div className="border-l-2 border-gray-200 pl-4 dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <span className="font-mono text-sm font-bold text-gray-900 dark:text-gray-100">
          v{release.version}
        </span>
        <span className="text-xs text-gray-400">{release.date}</span>
        {hasBreaking && (
          <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-bold text-red-700 dark:bg-red-900/30 dark:text-red-400">
            BREAKING
          </span>
        )}
      </div>
      {release.summary && (
        <p className="mb-2 text-xs text-gray-600 dark:text-gray-400">{release.summary}</p>
      )}
      <ul className="space-y-1.5">
        {release.entries.map((entry, i) => (
          <li key={i} className="flex items-start gap-2">
            <CategoryBadge category={entry.category} />
            <span
              className={`text-xs ${entry.breaking ? "font-semibold text-red-700 dark:text-red-400" : "text-gray-700 dark:text-gray-300"}`}
            >
              {entry.breaking && "⚠ "}
              {entry.description}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ChangelogCard({ releases, appName }: ChangelogCardProps) {
  const totalEntries = releases.reduce((s, r) => s + r.entries.length, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Changelog</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {releases.length} release{releases.length !== 1 ? "s" : ""} · {totalEntries} change
          {totalEntries !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Releases */}
      {releases.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No releases yet</p>
      ) : (
        <div className="space-y-5">
          {releases.map((r) => (
            <ReleaseSection key={r.version} release={r} />
          ))}
        </div>
      )}
    </div>
  );
}

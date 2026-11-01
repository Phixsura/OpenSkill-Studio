"use client";

interface SummaryInfo { total_versions: number; total_entries: number; breaking_changes: number; total_subscribers: number; total_reactions: number; total_comments: number; }
interface Props { summary: SummaryInfo; appName: string; }

export default function APIDeveloperAPIChangelogSummaryCard({ summary: s, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Changelog Summary</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Versions", v: s.total_versions },
          { l: "Entries", v: s.total_entries },
          { l: "Breaking", v: s.breaking_changes },
          { l: "Subscribers", v: s.total_subscribers },
          { l: "Reactions", v: s.total_reactions },
          { l: "Comments", v: s.total_comments },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

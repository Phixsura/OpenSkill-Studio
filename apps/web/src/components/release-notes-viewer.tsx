"use client";

interface ReleaseNotesViewerProps { version: string; sections: Record<string, string[]>;
  prCount: number; contributorCount: number; contributors: string[]; }

const SECTION_ICONS: Record<string, string> = {
  feature: "✨", bugfix: "🐛", improvement: "📈", breaking: "⚠️", docs: "📝",
};

export function ReleaseNotesViewer({ version, sections, prCount, contributorCount, contributors }: ReleaseNotesViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Release v{version}</h3>
        <span className="text-xs text-gray-400">{prCount} PRs · {contributorCount} contributors</span>
      </div>
      <div className="p-4 space-y-3">
        {Object.entries(sections).map(([section, items]) => (
          <div key={section}>
            <h4 className="text-sm font-medium mb-1">{SECTION_ICONS[section] ?? "📦"} {section}</h4>
            {items.map((item, i) => (
              <div key={i} className="text-xs text-gray-600 dark:text-gray-300 pl-4 py-0.5">• {item}</div>
            ))}
          </div>
        ))}
      </div>
      <div className="px-4 py-2 border-t dark:border-gray-700 text-[10px] text-gray-400">
        Contributors: {contributors.join(", ")}
      </div>
    </div>
  );
}

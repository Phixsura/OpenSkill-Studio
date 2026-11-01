"use client";

interface ChangelogViewerProps { version: string; sections: Record<string, string[]>;
  commitCount: number; }

const SECTION_ICONS: Record<string, string> = {
  Features: "✨", "Bug Fixes": "🐛", Performance: "⚡", Documentation: "📝",
  Refactoring: "♻️", Chores: "🔧", Other: "📦",
};

export function ChangelogViewer({ version, sections, commitCount }: ChangelogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Changelog v{version}</h3>
        <span className="text-xs text-gray-400">{commitCount} commits</span>
      </div>
      <div className="p-4 space-y-4">
        {Object.entries(sections).map(([section, items]) => (
          <div key={section}>
            <h4 className="text-sm font-medium mb-1">{SECTION_ICONS[section] ?? "📦"} {section}</h4>
            <ul className="space-y-0.5">
              {items.map((item, i) => (
                <li key={i} className="text-xs text-gray-600 dark:text-gray-300 pl-4">• {item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

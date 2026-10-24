"use client";

interface ChangelogSection { type: string; label: string; items: string[]; }
interface DeployChangelogViewerProps { version: string; deployer: string;
  sections: ChangelogSection[]; commitCount: number; }

const TYPE_ICONS: Record<string, string> = {
  feat: "✨", fix: "🐛", perf: "⚡", docs: "📝", other: "📦",
};

export function DeployChangelogViewer({ version, deployer, sections, commitCount }: DeployChangelogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Deploy Changelog v{version}</h3>
        <span className="text-xs text-gray-400">{commitCount} commits · {deployer}</span>
      </div>
      <div className="p-4 space-y-3">
        {sections.map(s => (
          <div key={s.type}>
            <h4 className="text-sm font-medium mb-1">{TYPE_ICONS[s.type] ?? "📦"} {s.label}</h4>
            {s.items.map((item, i) => (
              <div key={i} className="text-xs text-gray-600 dark:text-gray-300 pl-4 py-0.5">• {item}</div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

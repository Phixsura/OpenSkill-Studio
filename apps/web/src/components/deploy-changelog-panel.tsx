"use client";
interface ChangelogEntry { version: string; env: string; features: number; fixes: number; deployer: string; }
interface DeployChangelogPanelProps { entries: ChangelogEntry[]; totalFeatures: number; totalFixes: number; }
export function DeployChangelogPanel({ entries, totalFeatures, totalFixes }: DeployChangelogPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Deploy Changelog</h3>
        <span className="text-xs text-gray-400">{entries.length} deploys · {totalFeatures} features · {totalFixes} fixes</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.version} className="flex justify-between px-4 py-1.5 text-xs">
            <div>
              <span className="font-bold">{e.version}</span>
              <span className="text-gray-400 ml-2">{e.env} · {e.deployer}</span>
            </div>
            <span className="text-gray-400">✨{e.features} 🐛{e.fixes}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

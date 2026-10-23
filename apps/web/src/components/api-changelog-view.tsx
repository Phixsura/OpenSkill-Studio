"use client";

interface Entry { endpoint: string; description: string; icon: string; label: string; }
interface Section { type: string; label: string; icon: string; entries: Entry[]; }
interface ApiChangelogViewProps { version: string; sections: Section[]; totalChanges: number; hasBreaking: boolean; }

export function ApiChangelogView({ version, sections, totalChanges, hasBreaking }: ApiChangelogViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Changelog — {version}</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{totalChanges} changes</span>
          {hasBreaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
        </div>
      </div>
      {sections.map(s => (
        <div key={s.type}>
          <h3 className="flex items-center gap-1 text-sm font-medium">
            <span>{s.icon}</span> {s.label}
          </h3>
          <div className="ml-6 mt-1 space-y-1">
            {s.entries.map((e, i) => (
              <div key={i} className="text-sm">
                {e.endpoint && <code className="mr-1 text-xs text-blue-500">{e.endpoint}</code>}
                <span className="text-gray-500">{e.description}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

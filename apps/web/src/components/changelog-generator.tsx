"use client";

interface Entry { type: string; scope: string | null; description: string; icon: string; }
interface Section { type: string; label: string; icon: string; entries: Entry[]; }
interface ChangelogGeneratorProps { sections: Section[]; totalCommits: number;
  parsed: number; breaking: string[]; hasBreaking: boolean; }

export function ChangelogGenerator({ sections, totalCommits, parsed, breaking, hasBreaking }: ChangelogGeneratorProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Generated Changelog</h3>
        <span className="text-xs text-gray-400">{parsed}/{totalCommits} parsed</span>
      </div>
      {hasBreaking && (
        <div className="rounded-lg border-l-4 border-red-500 bg-red-50 p-3 dark:bg-red-900/10">
          <p className="text-xs font-semibold text-red-700 dark:text-red-400">💥 Breaking Changes</p>
          {breaking.map((b, i) => <p key={i} className="text-sm mt-1">{b}</p>)}
        </div>
      )}
      {sections.map(s => (
        <div key={s.type}>
          <h4 className="flex items-center gap-1.5 text-sm font-semibold mb-2">{s.icon} {s.label}</h4>
          <ul className="space-y-1 pl-5">
            {s.entries.map((e, i) => (
              <li key={i} className="text-sm">
                {e.scope && <span className="text-xs text-gray-400 font-mono">({e.scope}) </span>}
                {e.description}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

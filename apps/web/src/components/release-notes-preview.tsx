"use client";

interface Section { title: string; items: string[]; }
interface ReleaseNotesPreviewProps { version: string; sections: Section[]; totalCommits: number; }

export function ReleaseNotesPreview({ version, sections, totalCommits }: ReleaseNotesPreviewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h2 className="text-lg font-bold">Release {version}</h2>
      <p className="text-xs text-gray-400">{totalCommits} commits</p>
      <div className="mt-4 space-y-4">
        {sections.map((s, i) => (
          <div key={i}>
            <h3 className="text-sm font-semibold">{s.title}</h3>
            <ul className="mt-1 list-inside list-disc text-sm text-gray-600 dark:text-gray-400">
              {s.items.map((item, j) => <li key={j}>{item}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

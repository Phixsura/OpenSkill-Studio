"use client";

interface Section { title: string; items: string[]; }
interface ReleaseNotesPreviewProps { appName: string; version: string; sections: Section[];
  commitCount: number; onPublish: () => void; onEdit: () => void; }

export function ReleaseNotesPreview({ appName, version, sections, commitCount, onPublish, onEdit }: ReleaseNotesPreviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">{appName} v{version}</h2>
          <p className="text-xs text-gray-400">{commitCount} commits</p>
        </div>
        <div className="flex gap-2">
          <button onClick={onEdit} className="rounded border px-3 py-1.5 text-sm dark:border-gray-600">Edit</button>
          <button onClick={onPublish} className="rounded bg-green-600 px-3 py-1.5 text-sm text-white">Publish</button>
        </div>
      </div>
      {sections.map(s => (
        <div key={s.title}>
          <h3 className="text-sm font-semibold">{s.title}</h3>
          <ul className="mt-1 list-inside list-disc text-sm text-gray-600 dark:text-gray-300">
            {s.items.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}

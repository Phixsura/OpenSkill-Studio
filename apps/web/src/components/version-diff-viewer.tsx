"use client";

interface DiffSection { added: string[]; removed: string[]; }
interface VersionDiffViewerProps { fromVersion: string; toVersion: string; permissions: DiffSection; endpoints: DiffSection; config: DiffSection; hasBreaking: boolean; }

export function VersionDiffViewer({ fromVersion, toVersion, permissions, endpoints, config, hasBreaking }: VersionDiffViewerProps) {
  const sections = [
    { label: "Permissions", diff: permissions },
    { label: "Endpoints", diff: endpoints },
    { label: "Config", diff: config },
  ];

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{fromVersion} → {toVersion}</h3>
        {hasBreaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">Breaking</span>}
      </div>
      <div className="mt-3 space-y-3">
        {sections.map(s => (s.diff.added.length > 0 || s.diff.removed.length > 0) && (
          <div key={s.label}>
            <p className="text-xs font-medium text-gray-500">{s.label}</p>
            {s.diff.added.map(a => <p key={a} className="text-xs text-green-600">+ {a}</p>)}
            {s.diff.removed.map(r => <p key={r} className="text-xs text-red-600">- {r}</p>)}
          </div>
        ))}
      </div>
    </div>
  );
}

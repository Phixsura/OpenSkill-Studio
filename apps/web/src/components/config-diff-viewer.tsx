"use client";

interface ConfigDiffViewerProps {
  added: Record<string, unknown>;
  removed: Record<string, unknown>;
  changed: Record<string, { from: unknown; to: unknown }>;
}

export function ConfigDiffViewer({ added, removed, changed }: ConfigDiffViewerProps) {
  const hasChanges = Object.keys(added).length + Object.keys(removed).length + Object.keys(changed).length > 0;
  if (!hasChanges) return <p className="py-3 text-center text-sm text-gray-400">No config changes</p>;

  return (
    <div className="space-y-2 text-sm">
      {Object.entries(added).map(([k, v]) => (
        <div key={k} className="flex gap-2 rounded bg-green-50 p-2 dark:bg-green-900/20">
          <span className="text-green-600">+</span><code>{k}</code><span className="text-gray-500">= {JSON.stringify(v)}</span>
        </div>
      ))}
      {Object.entries(removed).map(([k, v]) => (
        <div key={k} className="flex gap-2 rounded bg-red-50 p-2 dark:bg-red-900/20">
          <span className="text-red-600">-</span><code>{k}</code><span className="text-gray-500">= {JSON.stringify(v)}</span>
        </div>
      ))}
      {Object.entries(changed).map(([k, v]) => (
        <div key={k} className="flex gap-2 rounded bg-yellow-50 p-2 dark:bg-yellow-900/20">
          <span className="text-yellow-600">~</span><code>{k}</code>
          <span className="text-red-500 line-through">{JSON.stringify(v.from)}</span>
          <span>→</span>
          <span className="text-green-600">{JSON.stringify(v.to)}</span>
        </div>
      ))}
    </div>
  );
}

"use client";

interface ManifestError { field: string; error: string; }
interface ManifestDiff { added: string[]; removed: string[]; changed: { service: string; newImage: string }[]; }
interface DeployManifestViewerProps { valid: boolean; errors: ManifestError[];
  serviceCount: number; diff?: ManifestDiff; }

export function DeployManifestViewer({ valid, errors, serviceCount, diff }: DeployManifestViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Deploy Manifest</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} errors`} · {serviceCount} services
        </span>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{e.field}</span>: {e.error}
            </div>
          ))}
        </div>
      )}
      {diff && diff.added.length + diff.removed.length + diff.changed.length > 0 && (
        <div className="border-t dark:border-gray-700 p-3 text-xs font-mono space-y-0.5">
          {diff.added.map(a => <div key={a} className="text-green-600">+ {a}</div>)}
          {diff.removed.map(r => <div key={r} className="text-red-600">- {r}</div>)}
          {diff.changed.map(c => <div key={c.service} className="text-yellow-600">~ {c.service} → {c.newImage}</div>)}
        </div>
      )}
    </div>
  );
}

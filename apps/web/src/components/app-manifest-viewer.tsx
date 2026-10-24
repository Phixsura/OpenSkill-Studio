"use client";

interface AppManifestViewerProps { manifest: Record<string, unknown>; valid: boolean;
  errors: string[]; warnings: string[]; }

export function AppManifestViewer({ manifest, valid, errors, warnings }: AppManifestViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">app.json</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? "✓ Valid" : `✗ ${errors.length} errors`}
        </span>
      </div>
      {errors.map((e, i) => <p key={`e${i}`} className="text-xs text-red-500">❌ {e}</p>)}
      {warnings.map((w, i) => <p key={`w${i}`} className="text-xs text-yellow-600">⚠ {w}</p>)}
      <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 overflow-x-auto max-h-48">
        {JSON.stringify(manifest, null, 2)}
      </pre>
    </div>
  );
}

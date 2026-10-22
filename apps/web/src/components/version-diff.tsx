"use client";

interface VersionDiffProps {
  diff: {
    version_from: string;
    version_to: string;
    breaking: boolean;
    permissions: { added: string[]; removed: string[] };
    events: { added: string[]; removed: string[] };
    secrets: { added: string[]; removed: string[] };
    ui_extensions: { added: string[]; removed: string[] };
    sandbox: { changed: boolean };
    config_schema_changed: boolean;
    summary: string;
  };
}

export function VersionDiff({ diff }: VersionDiffProps) {
  return (
    <div className={`rounded-lg border p-4 ${diff.breaking ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/20" : "border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-900/20"}`}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">
          {diff.version_from} → {diff.version_to}
        </h3>
        {diff.breaking ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
            Breaking
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
            Compatible
          </span>
        )}
      </div>

      <p className="mb-3 text-sm text-gray-600 dark:text-gray-400">{diff.summary}</p>

      {diff.permissions.added.length > 0 && (
        <div className="mb-2">
          <span className="text-xs font-medium text-green-700 dark:text-green-300">+ Permissions:</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {diff.permissions.added.map((p) => (
              <span key={p} className="rounded bg-green-100 px-1.5 py-0.5 text-xs dark:bg-green-900">{p}</span>
            ))}
          </div>
        </div>
      )}

      {diff.permissions.removed.length > 0 && (
        <div className="mb-2">
          <span className="text-xs font-medium text-red-700 dark:text-red-300">- Permissions:</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {diff.permissions.removed.map((p) => (
              <span key={p} className="rounded bg-red-100 px-1.5 py-0.5 text-xs dark:bg-red-900">{p}</span>
            ))}
          </div>
        </div>
      )}

      {diff.sandbox.changed && (
        <p className="text-xs text-yellow-700 dark:text-yellow-300">⚙️ Sandbox configuration changed</p>
      )}
      {diff.config_schema_changed && (
        <p className="text-xs text-yellow-700 dark:text-yellow-300">📋 Config schema changed</p>
      )}
    </div>
  );
}

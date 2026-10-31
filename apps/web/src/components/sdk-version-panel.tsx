"use client";

interface SDKRelease {
  version: string;
  status: "stable" | "beta" | "deprecated" | "end_of_life";
  minPlatform: string;
  maxPlatform: string;
  releaseDate: string;
  deprecationMessage?: string;
}

interface UpgradePath {
  fromVersion: string;
  toVersion: string;
  steps: string[];
  hasBreaking: boolean;
}

const statusStyles: Record<string, { color: string; label: string }> = {
  stable: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Stable" },
  beta: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", label: "Beta" },
  deprecated: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Deprecated" },
  end_of_life: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", label: "EOL" },
};

export function SDKVersionPanel({
  releases,
  currentVersion,
  recommendedVersion,
  upgradePath,
  onUpgrade,
}: {
  releases: SDKRelease[];
  currentVersion: string;
  recommendedVersion?: string;
  upgradePath?: UpgradePath;
  onUpgrade?: (version: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 SDK Versions</h2>
        <span className="text-sm text-gray-500">Current: <code className="font-bold">{currentVersion}</code></span>
      </div>

      {recommendedVersion && recommendedVersion !== currentVersion && (
        <div className="rounded-lg border border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/10 p-3 flex items-center justify-between">
          <div>
            <span className="text-sm font-medium">⬆️ Upgrade available: <code>{recommendedVersion}</code></span>
            {upgradePath?.hasBreaking && (
              <span className="text-xs text-yellow-600 ml-2">⚠ Breaking changes</span>
            )}
          </div>
          <button onClick={() => onUpgrade?.(recommendedVersion)}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg">Upgrade</button>
        </div>
      )}

      {upgradePath && (
        <div className="rounded-lg border dark:border-gray-700 p-3">
          <span className="text-sm font-medium">Migration Steps ({upgradePath.fromVersion} → {upgradePath.toVersion})</span>
          <ol className="mt-1 space-y-1">
            {upgradePath.steps.map((step, i) => (
              <li key={i} className="text-xs text-gray-600 dark:text-gray-400 flex gap-2">
                <span className="text-blue-500 font-bold">{i + 1}.</span> {step}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="space-y-1">
        {releases.map((r) => {
          const cfg = statusStyles[r.status];
          const isCurrent = r.version === currentVersion;
          return (
            <div key={r.version}
              className={`rounded-lg border p-3 flex items-center justify-between ${isCurrent ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
              <div className="flex items-center gap-2">
                <code className="text-sm font-bold">{r.version}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                {isCurrent && <span className="text-xs text-blue-600 font-medium">current</span>}
                <span className="text-xs text-gray-400">{r.releaseDate}</span>
              </div>
              <span className="text-xs text-gray-400">{r.minPlatform}–{r.maxPlatform}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

interface CompatEntry {
  app_id: string;
  app_version: string;
  platform_version: string;
  status: "compatible" | "degraded" | "incompatible" | "untested";
  notes: string;
}

interface ImpactReport {
  platform_version: string;
  compatible: CompatEntry[];
  degraded: CompatEntry[];
  incompatible: CompatEntry[];
  untested: string[];
  safe_to_upgrade: boolean;
}

interface CompatibilityMatrixViewProps {
  impact: ImpactReport;
  currentPlatform: string;
}

const STATUS_STYLES: Record<string, { label: string; color: string; icon: string }> = {
  compatible: {
    label: "Compatible",
    color: "text-green-700 bg-green-100 dark:bg-green-900/20 dark:text-green-300",
    icon: "✓",
  },
  degraded: {
    label: "Degraded",
    color: "text-yellow-700 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-300",
    icon: "⚠",
  },
  incompatible: {
    label: "Incompatible",
    color: "text-red-700 bg-red-100 dark:bg-red-900/20 dark:text-red-300",
    icon: "✗",
  },
  untested: {
    label: "Untested",
    color: "text-gray-500 bg-gray-100 dark:bg-gray-800 dark:text-gray-400",
    icon: "?",
  },
};

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.untested;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold ${s.color}`}
    >
      {s.icon} {s.label}
    </span>
  );
}

function AppRow({ entry }: { entry: CompatEntry }) {
  return (
    <div className="flex items-center justify-between py-1.5 text-xs">
      <div className="flex items-center gap-2">
        <span className="font-medium">{entry.app_id}</span>
        <code className="text-gray-400">v{entry.app_version}</code>
      </div>
      <div className="flex items-center gap-2">
        {entry.notes && <span className="max-w-[200px] truncate text-gray-400">{entry.notes}</span>}
        <StatusBadge status={entry.status} />
      </div>
    </div>
  );
}

export function CompatibilityMatrixView({ impact, currentPlatform }: CompatibilityMatrixViewProps) {
  const totalApps =
    impact.compatible.length +
    impact.degraded.length +
    impact.incompatible.length +
    impact.untested.length;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Platform Upgrade Impact</h3>
            <p className="text-xs text-gray-500">
              {currentPlatform} → {impact.platform_version} • {totalApps} apps affected
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${impact.safe_to_upgrade ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"}`}
          >
            {impact.safe_to_upgrade ? "✓ Safe to Upgrade" : "⚠ Upgrade Blocked"}
          </span>
        </div>
      </div>

      {/* Summary bar */}
      <div className="flex gap-3 border-b border-gray-200 px-4 py-2 text-xs dark:border-gray-700">
        <span className="text-green-600">{impact.compatible.length} compatible</span>
        <span className="text-yellow-600">{impact.degraded.length} degraded</span>
        <span className="text-red-600">{impact.incompatible.length} incompatible</span>
        <span className="text-gray-500">{impact.untested.length} untested</span>
      </div>

      {/* Incompatible (most important) */}
      {impact.incompatible.length > 0 && (
        <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
          <p className="text-[10px] font-semibold uppercase text-red-600">
            Incompatible — must upgrade before platform update
          </p>
          <div className="mt-1 divide-y divide-gray-100 dark:divide-gray-800">
            {impact.incompatible.map((e) => (
              <AppRow key={`${e.app_id}-${e.app_version}`} entry={e} />
            ))}
          </div>
        </div>
      )}

      {/* Degraded */}
      {impact.degraded.length > 0 && (
        <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
          <p className="text-[10px] font-semibold uppercase text-yellow-600">
            Degraded — will work with issues
          </p>
          <div className="mt-1 divide-y divide-gray-100 dark:divide-gray-800">
            {impact.degraded.map((e) => (
              <AppRow key={`${e.app_id}-${e.app_version}`} entry={e} />
            ))}
          </div>
        </div>
      )}

      {/* Untested */}
      {impact.untested.length > 0 && (
        <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
          <p className="text-[10px] font-semibold uppercase text-gray-500">Untested</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {impact.untested.map((id) => (
              <code
                key={id}
                className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800"
              >
                {id}
              </code>
            ))}
          </div>
        </div>
      )}

      {/* Compatible */}
      {impact.compatible.length > 0 && (
        <div className="px-4 py-2">
          <p className="text-[10px] font-semibold uppercase text-green-600">Compatible</p>
          <div className="mt-1 divide-y divide-gray-100 dark:divide-gray-800">
            {impact.compatible.map((e) => (
              <AppRow key={`${e.app_id}-${e.app_version}`} entry={e} />
            ))}
          </div>
        </div>
      )}

      {totalApps === 0 && (
        <div className="py-6 text-center text-sm text-gray-500">No installed apps to analyze</div>
      )}
    </div>
  );
}

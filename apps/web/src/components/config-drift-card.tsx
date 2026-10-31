"use client";

interface DriftEntryInfo {
  key: string;
  drift_type: "added" | "removed" | "changed";
  source_value: string | null;
  target_value: string | null;
}

interface DriftReportInfo {
  source_env: string;
  target_env: string;
  drifts: DriftEntryInfo[];
}

interface ConfigDriftCardProps {
  report: DriftReportInfo | null;
  environments: string[];
  appName: string;
}

const driftBadge: Record<string, string> = {
  added: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  removed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  changed: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function ConfigDriftCard({ report, environments, appName }: ConfigDriftCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔀 Config Drift
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{environments.length} envs</span>
      </div>

      {!report ? (
        <p className="text-center text-sm text-gray-400">No drift report</p>
      ) : (
        <>
          <div className="mb-3 flex items-center justify-center gap-2 text-xs text-gray-500">
            <span className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">
              {report.source_env}
            </span>
            <span>→</span>
            <span className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">
              {report.target_env}
            </span>
          </div>

          {report.drifts.length === 0 ? (
            <p className="text-center text-sm text-green-600 dark:text-green-400">
              No drift detected
            </p>
          ) : (
            <div className="space-y-1.5">
              <p className="text-xs text-gray-500">{report.drifts.length} differences</p>
              {report.drifts.map((d) => (
                <div
                  key={d.key}
                  className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
                >
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {d.key}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${driftBadge[d.drift_type] ?? ""}`}
                  >
                    {d.drift_type}
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

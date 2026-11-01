"use client";

interface CompatibilityReportProps {
  report: {
    from_version: string;
    to_version: string;
    compatible: boolean;
    breaking_changes: string[];
    warnings: string[];
    permissions_added: string[];
    permissions_removed: string[];
  };
}

/**
 * CompatibilityReport — displays the result of a version compatibility check.
 */
export function CompatibilityReport({ report }: CompatibilityReportProps) {
  return (
    <div
      className={`rounded-lg border p-5 ${
        report.compatible
          ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20"
          : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"
      }`}
    >
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">
          Compatibility: v{report.from_version} → v{report.to_version}
        </h3>
        <span
          className={`rounded-full px-3 py-0.5 text-sm font-medium ${
            report.compatible
              ? "bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200"
              : "bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200"
          }`}
        >
          {report.compatible ? "✅ Compatible" : "❌ Breaking Changes"}
        </span>
      </div>

      {/* Breaking changes */}
      {report.breaking_changes.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 text-sm font-medium text-red-700 dark:text-red-400">
            Breaking Changes:
          </p>
          <ul className="list-inside list-disc space-y-1 text-sm text-red-600 dark:text-red-400">
            {report.breaking_changes.map((bc, i) => (
              <li key={i}>{bc}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {report.warnings.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 text-sm font-medium text-yellow-700 dark:text-yellow-400">
            Warnings:
          </p>
          <ul className="list-inside list-disc space-y-1 text-sm text-yellow-600 dark:text-yellow-400">
            {report.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Permission changes */}
      {(report.permissions_added.length > 0 || report.permissions_removed.length > 0) && (
        <div className="flex gap-4 text-sm">
          {report.permissions_added.length > 0 && (
            <div>
              <span className="font-medium text-blue-600">+ Added: </span>
              {report.permissions_added.map((p) => (
                <code
                  key={p}
                  className="mr-1 rounded bg-blue-100 px-1.5 py-0.5 text-xs dark:bg-blue-900"
                >
                  {p}
                </code>
              ))}
            </div>
          )}
          {report.permissions_removed.length > 0 && (
            <div>
              <span className="font-medium text-orange-600">− Removed: </span>
              {report.permissions_removed.map((p) => (
                <code
                  key={p}
                  className="mr-1 rounded bg-orange-100 px-1.5 py-0.5 text-xs dark:bg-orange-900"
                >
                  {p}
                </code>
              ))}
            </div>
          )}
        </div>
      )}

      {report.compatible &&
        report.warnings.length === 0 &&
        report.breaking_changes.length === 0 && (
          <p className="text-sm text-green-600 dark:text-green-400">
            No breaking changes or warnings. Safe to upgrade.
          </p>
        )}
    </div>
  );
}

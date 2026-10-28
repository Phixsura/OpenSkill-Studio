"use client";

interface ValidationIssueInfo {
  field: string;
  message: string;
}

interface RequestValidatorCardProps {
  schemaId: string;
  valid: boolean;
  issues: ValidationIssueInfo[];
  fieldCount: number;
  appName: string;
}

export default function RequestValidatorCard({
  schemaId,
  valid,
  issues,
  fieldCount,
  appName,
}: RequestValidatorCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Request Validation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {schemaId}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{fieldCount} fields</span>
          {valid ? (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              ✓ Valid
            </span>
          ) : (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              ✕ {issues.length} issues
            </span>
          )}
        </div>
      </div>

      {valid && issues.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">
          All fields validated
        </p>
      ) : (
        <div className="space-y-1.5">
          {issues.map((i, idx) => (
            <div
              key={`${i.field}-${idx}`}
              className="flex items-start gap-2 rounded bg-red-50 px-2.5 py-1.5 dark:bg-red-950/20"
            >
              <span className="mt-0.5 text-xs text-red-500">✕</span>
              <div>
                <span className="font-mono text-xs font-medium text-red-700 dark:text-red-400">
                  {i.field}
                </span>
                <p className="text-[11px] text-red-600/80 dark:text-red-400/70">{i.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

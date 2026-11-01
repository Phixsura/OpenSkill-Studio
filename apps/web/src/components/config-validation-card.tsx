"use client";

interface ValidationError {
  field: string;
  message: string;
  value?: unknown;
}

interface ConfigValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: string[];
  schema_id: string;
}

interface ConfigValidationCardProps {
  result: ConfigValidationResult;
  appName: string;
}

function ErrorRow({ error }: { error: ValidationError }) {
  return (
    <li className="flex items-start gap-2 py-1.5">
      <span className="mt-0.5 text-red-500">✕</span>
      <div className="min-w-0 flex-1">
        <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">
          {error.field}
        </span>
        <p className="text-xs text-red-600 dark:text-red-400">{error.message}</p>
        {error.value !== undefined && error.value !== null && (
          <p className="truncate text-[11px] text-gray-400">Value: {JSON.stringify(error.value)}</p>
        )}
      </div>
    </li>
  );
}

function WarningRow({ warning }: { warning: string }) {
  return (
    <li className="flex items-center gap-2 py-1">
      <span className="text-yellow-500">⚠</span>
      <span className="text-xs text-yellow-700 dark:text-yellow-400">{warning}</span>
    </li>
  );
}

export default function ConfigValidationCard({ result, appName }: ConfigValidationCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Config Validation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {result.schema_id}
          </p>
        </div>
        {result.valid ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            ✓ Valid
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            ✕ {result.errors.length} error{result.errors.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {/* Errors */}
      {result.errors.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 text-xs font-medium text-red-600 dark:text-red-400">Errors</p>
          <ul className="divide-y divide-gray-100 dark:divide-gray-800">
            {result.errors.map((e, i) => (
              <ErrorRow key={`${e.field}-${i}`} error={e} />
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-medium text-yellow-600 dark:text-yellow-400">Warnings</p>
          <ul>
            {result.warnings.map((w, i) => (
              <WarningRow key={i} warning={w} />
            ))}
          </ul>
        </div>
      )}

      {/* All clear */}
      {result.valid && result.warnings.length === 0 && (
        <p className="text-center text-sm text-green-600 dark:text-green-400">
          All configuration fields are valid
        </p>
      )}
    </div>
  );
}

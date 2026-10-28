"use client";

interface SchemaInfo {
  event_type: string;
  required_count: number;
  optional_count: number;
  success_rate: number;
  total_checks: number;
}

interface PayloadValidatorCardProps {
  schemas: SchemaInfo[];
  appName: string;
}

export default function PayloadValidatorCard({ schemas, appName }: PayloadValidatorCardProps) {
  const failing = schemas.filter((s) => s.success_rate < 100 && s.total_checks > 0).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Payload Validation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{schemas.length} schemas</span>
          {failing > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {failing} failing
            </span>
          )}
        </div>
      </div>

      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No payload schemas</p>
      ) : (
        <div className="space-y-1.5">
          {schemas.map((s) => (
            <div
              key={s.event_type}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                  {s.event_type}
                </span>
                <span className="text-[10px] text-gray-400">
                  {s.required_count}req {s.optional_count}opt
                </span>
              </div>
              <span
                className={`text-xs font-medium ${s.success_rate >= 100 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
              >
                {s.success_rate}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

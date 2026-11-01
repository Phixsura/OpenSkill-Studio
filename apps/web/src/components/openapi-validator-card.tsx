"use client";

interface EndpointComplianceInfo {
  method: string;
  path: string;
  compliance_pct: number;
  total_checks: number;
  last_violations: string[];
}

interface OpenAPIValidatorCardProps {
  endpoints: EndpointComplianceInfo[];
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

export default function OpenAPIValidatorCard({ endpoints, appName }: OpenAPIValidatorCardProps) {
  const failing = endpoints.filter((e) => e.compliance_pct < 100).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Contract</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {failing > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {failing} failing
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All compliant
          </span>
        )}
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints validated</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((e) => (
            <div
              key={`${e.method}-${e.path}`}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${METHOD_COLORS[e.method] ?? "bg-gray-100 text-gray-600"}`}
                  >
                    {e.method}
                  </span>
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {e.path}
                  </span>
                </div>
                <span
                  className={`text-xs font-medium ${e.compliance_pct >= 100 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
                >
                  {e.compliance_pct}%
                </span>
              </div>
              {e.last_violations.length > 0 && (
                <div className="mt-1 text-[10px] text-red-500">
                  {e.last_violations.slice(0, 2).join(" · ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

interface EnvVarInfo {
  key: string;
  value: string;
  sensitive: boolean;
  environment: string;
}

interface EnvVariableCardProps {
  variables: EnvVarInfo[];
  environments: string[];
  appName: string;
}

export default function EnvVariableCard({
  variables,
  environments,
  appName,
}: EnvVariableCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⚙️ Environment Variables
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {variables.length} vars · {environments.length} envs
        </span>
      </div>

      {variables.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No variables</p>
      ) : (
        <div className="space-y-1">
          {variables.map((v) => (
            <div
              key={`${v.environment}-${v.key}`}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{v.key}</span>
                {v.sensitive && <span className="text-[9px] text-orange-500">🔒</span>}
              </div>
              <div className="flex items-center gap-2 text-[10px] text-gray-400">
                <span className="font-mono">{v.value}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] dark:bg-gray-800">
                  {v.environment}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

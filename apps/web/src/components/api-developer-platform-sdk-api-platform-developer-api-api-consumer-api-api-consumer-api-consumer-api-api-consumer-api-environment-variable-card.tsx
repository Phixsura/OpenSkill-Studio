"use client";

interface Variable { key: string; value: string; sensitive: boolean; updatedAt: string; }
interface Props { variables: Variable[]; environment: string; consumerId: string; appName: string; }

const envColors: Record<string, string> = {
  production: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  staging: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  development: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariableCard({ variables, environment, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Environment Variables</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${envColors[environment] ?? ""}`}>{environment}</span>
      </div>
      {variables.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No variables</p>
      ) : (
        <div className="space-y-1">
          {variables.map((v) => (
            <div key={v.key} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="font-medium text-gray-700 dark:text-gray-300">{v.key}</code>
              <span className={v.sensitive ? "text-gray-400 italic" : "text-gray-500"}>{v.sensitive ? "•••••" : v.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

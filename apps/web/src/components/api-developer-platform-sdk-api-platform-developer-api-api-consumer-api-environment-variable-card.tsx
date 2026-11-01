"use client";

interface VarInfo { key: string; value: string; secret: boolean; }
interface Props { vars: VarInfo[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariableCard({ vars: envVars, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Environment Variables</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {envVars.length} vars</p>
      </div>
      {envVars.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No environment variables</p>
      ) : (
        <div className="space-y-1">
          {envVars.map((v) => (
            <div key={v.key} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{v.key}</span>
              <span className={`font-mono ${v.secret ? "text-amber-500" : "text-gray-400"}`}>{v.secret ? "🔒 " : ""}{v.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

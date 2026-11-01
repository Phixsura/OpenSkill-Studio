"use client";

interface Props { consumerId: string; algorithm: string; headerName: string; includeBody: boolean; includePath: boolean; configured: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigningCard({ consumerId, algorithm, headerName, includeBody, includePath, configured, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✍️ Request Signing</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${configured ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-gray-200 text-gray-500"}`}>{configured ? "Configured" : "Not Set"}</span>
      </div>
      {configured && (
        <div className="space-y-1 text-[11px]">
          <div className="flex justify-between"><span className="text-gray-500">Algorithm:</span><span className="font-medium text-gray-700 dark:text-gray-300">{algorithm.toUpperCase()}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Header:</span><code className="text-gray-700 dark:text-gray-300">{headerName}</code></div>
          <div className="flex justify-between"><span className="text-gray-500">Include body:</span><span className={includeBody ? "text-green-500" : "text-gray-400"}>{includeBody ? "Yes" : "No"}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Include path:</span><span className={includePath ? "text-green-500" : "text-gray-400"}>{includePath ? "Yes" : "No"}</span></div>
        </div>
      )}
    </div>
  );
}

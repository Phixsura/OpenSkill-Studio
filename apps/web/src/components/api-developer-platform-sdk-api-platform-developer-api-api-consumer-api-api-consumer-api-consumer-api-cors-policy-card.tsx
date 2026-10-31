"use client";

interface Props { consumerId: string; allowedOrigins: string[]; allowedMethods: string[]; allowCredentials: boolean; maxAgeSec: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicyCard({ consumerId, allowedOrigins, allowedMethods, allowCredentials, maxAgeSec, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 CORS Policy</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="space-y-2 text-[11px]">
        <div>
          <span className="text-gray-500">Origins:</span>
          <div className="mt-0.5 flex flex-wrap gap-1">
            {allowedOrigins.map((o) => <span key={o} className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{o}</span>)}
          </div>
        </div>
        <div>
          <span className="text-gray-500">Methods: </span>
          {allowedMethods.map((m) => <span key={m} className="mr-1 text-gray-700 dark:text-gray-300">{m}</span>)}
        </div>
        <div className="flex gap-3 text-[10px] text-gray-400">
          <span>Credentials: {allowCredentials ? "Yes" : "No"}</span>
          <span>Max-Age: {maxAgeSec}s</span>
        </div>
      </div>
    </div>
  );
}

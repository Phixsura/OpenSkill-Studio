"use client";

interface Props { consumerId: string; timeoutMs: number; maxRequestSize: number; compression: boolean; cors: boolean; logLevel: string; blockedPaths: string[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfigCard({ consumerId, timeoutMs, maxRequestSize, compression, cors, logLevel, blockedPaths, appName }: Props) {
  const fmtSize = (b: number) => b >= 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${(b / 1024).toFixed(0)} KB`;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Gateway Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="space-y-1 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Timeout:</span><span className="text-gray-700 dark:text-gray-300">{timeoutMs}ms</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Max request:</span><span className="text-gray-700 dark:text-gray-300">{fmtSize(maxRequestSize)}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Compression:</span><span className={compression ? "text-green-500" : "text-gray-400"}>{compression ? "ON" : "OFF"}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">CORS:</span><span className={cors ? "text-green-500" : "text-gray-400"}>{cors ? "ON" : "OFF"}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Log level:</span><span className="text-gray-700 dark:text-gray-300">{logLevel}</span></div>
      </div>
      {blockedPaths.length > 0 && (
        <div className="mt-2">
          <span className="text-[10px] text-gray-400">Blocked:</span>
          <div className="flex flex-wrap gap-1 mt-0.5">{blockedPaths.map((p) => <code key={p} className="rounded bg-red-100 px-1 py-0.5 text-[9px] text-red-600 dark:bg-red-900/30 dark:text-red-400">{p}</code>)}</div>
        </div>
      )}
    </div>
  );
}

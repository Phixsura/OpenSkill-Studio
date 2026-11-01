"use client";

interface Contract { id: string; endpoint: string; method: string; assertionCount: number; lastResult: boolean | null; }
interface Props { contracts: Contract[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiContractTestCard({ contracts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 API Contracts</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {contracts.length} contracts</p>
      </div>
      {contracts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No contracts defined</p>
      ) : (
        <div className="space-y-1">
          {contracts.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className="font-bold text-blue-600">{c.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{c.endpoint}</code>
                <span className="text-[10px] text-gray-400">{c.assertionCount} assertions</span>
              </div>
              {c.lastResult !== null && <span className={c.lastResult ? "text-green-500" : "text-red-500"}>{c.lastResult ? "✅" : "❌"}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

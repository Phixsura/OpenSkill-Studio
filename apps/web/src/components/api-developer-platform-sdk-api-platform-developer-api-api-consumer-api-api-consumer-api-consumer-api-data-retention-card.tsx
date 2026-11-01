"use client";

interface Policy { dataType: string; retentionDays: number; archiveFirst: boolean; autoDelete: boolean; expired: boolean; }
interface Props { policies: Policy[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetentionCard({ policies, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗑️ Data Retention</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retention policies</p>
      ) : (
        <div className="space-y-1">
          {policies.map((p) => (
            <div key={p.dataType} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.dataType}</span>
                <span className="ml-1 text-[10px] text-gray-400">{p.retentionDays}d</span>
                {p.archiveFirst && <span className="ml-1 text-[9px] text-blue-400">archive</span>}
              </div>
              {p.expired ? <span className="text-[10px] text-red-500">Expired data</span> : <span className="text-[10px] text-green-500">OK</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

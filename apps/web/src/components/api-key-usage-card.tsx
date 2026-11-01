"use client";

interface KeyUsageInfo {
  key_id: string;
  total_requests: number;
  error_rate: number;
  top_endpoint: string;
}

interface APIKeyUsageCardProps {
  keys: KeyUsageInfo[];
  appName: string;
}

export default function APIKeyUsageCard({ keys, appName }: APIKeyUsageCardProps) {
  const totalReqs = keys.reduce((s, k) => s + k.total_requests, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 API Key Usage</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{keys.length} keys · {totalReqs.toLocaleString()} reqs</span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API key usage</p>
      ) : (
        <div className="space-y-1.5">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{k.key_id}</span>
                <p className="text-[10px] text-gray-400">{k.top_endpoint}</p>
              </div>
              <div className="text-right">
                <span className="text-xs font-medium text-gray-900 dark:text-gray-100">{k.total_requests.toLocaleString()}</span>
                <p className={`text-[10px] ${k.error_rate > 5 ? "text-red-500" : "text-gray-400"}`}>{k.error_rate}% err</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

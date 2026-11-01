"use client";

interface DevActivityInfo {
  developer_id: string;
  api_calls: number;
  active_days: number;
  endpoints_used: number;
  engagement_score: number;
}

interface APIDeveloperActivityCardProps {
  developers: DevActivityInfo[];
  totalActive: number;
  appName: string;
}

export default function APIDeveloperActivityCard({ developers, totalActive, appName }: APIDeveloperActivityCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👩‍💻 Developer Activity</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalActive} active devs</span>
      </div>

      {developers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No developer activity</p>
      ) : (
        <div className="space-y-1.5">
          {developers.map((d) => (
            <div key={d.developer_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <span className="text-xs text-gray-700 dark:text-gray-300">{d.developer_id}</span>
              <div className="text-[10px] text-gray-400">
                {d.api_calls} calls · {d.active_days}d · score {d.engagement_score}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

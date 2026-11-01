"use client";

interface PriorityInfo { consumer_id: string; priority_level: number; queue_position: string; }
interface Props { configs: PriorityInfo[]; appName: string; }

const posColor: Record<string, string> = { normal: "text-gray-400", high: "text-blue-600 dark:text-blue-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriorityCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 Request Priority</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} consumers</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No priorities configured</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <div className="flex items-center gap-2">
                <span className="font-bold text-gray-900 dark:text-gray-100">P{c.priority_level}</span>
                <span className={posColor[c.queue_position] ?? ""}>{c.queue_position}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

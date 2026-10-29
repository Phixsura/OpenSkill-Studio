"use client";

interface PriorityInfo { event_type: string; priority: number; delivery_count: number; }

interface APIWebhookPriorityCardProps { priorities: PriorityInfo[]; appName: string; }

const prioLabel: Record<number, string> = { 1: "Low", 2: "Normal", 3: "Medium", 4: "High", 5: "Critical" };
const prioColor: Record<number, string> = { 1: "text-gray-400", 2: "text-blue-500", 3: "text-yellow-600", 4: "text-orange-500", 5: "text-red-500" };

export default function APIWebhookPriorityCard({ priorities, appName }: APIWebhookPriorityCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔺 Webhook Priority</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{priorities.length} events</span>
      </div>
      {priorities.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No priorities configured</p>
      ) : (
        <div className="space-y-1">
          {priorities.map((p) => (
            <div key={p.event_type} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.event_type}</span>
              <span className={`font-medium ${prioColor[p.priority] ?? "text-gray-400"}`}>{prioLabel[p.priority] ?? `P${p.priority}`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

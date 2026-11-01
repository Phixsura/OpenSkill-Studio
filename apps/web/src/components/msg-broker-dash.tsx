"use client";

interface TopicInfo { name: string; subscribers: number; pendingMessages: number; }
interface MsgBrokerDashProps { topics: TopicInfo[]; totalDelivered: number; totalPending: number; }

export function MsgBrokerDash({ topics, totalDelivered, totalPending }: MsgBrokerDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📨 Message Broker</h3>
        <span className="text-xs text-gray-400">
          {totalDelivered.toLocaleString()} delivered · {totalPending} pending
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {topics.map(t => (
          <div key={t.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono font-semibold">{t.name}</span>
            <div className="flex items-center gap-3 text-gray-400">
              <span>{t.subscribers} subs</span>
              <span className={t.pendingMessages > 0 ? "text-yellow-600" : ""}>{t.pendingMessages} pending</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

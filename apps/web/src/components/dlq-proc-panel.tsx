"use client";
interface DlqMessage { id: string; error: string; attempts: number; }
interface DlqProcPanelProps { messages: DlqMessage[]; reprocessed: number; discarded: number; }
export function DlqProcPanel({ messages, reprocessed, discarded }: DlqProcPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📪 Dead Letter Queue</h3>
        <span className={`text-xs ${messages.length > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {messages.length} pending · {reprocessed} retried · {discarded} discarded
        </span>
      </div>
      {messages.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {messages.map(m => (
            <div key={m.id} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono">{m.id}</span>
              <span className="text-red-500">{m.error} (×{m.attempts})</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">Queue empty</div>
      )}
    </div>
  );
}

"use client";

interface CommsMessage { type: string; message: string; channels: string[]; }
interface IncCommsPanelProps { messages: CommsMessage[]; total: number; }

const TYPE_ICONS: Record<string, string> = {
  investigating: "🔍", identified: "🎯", monitoring: "👁️", resolved: "✅",
};

export function IncCommsPanel({ messages, total }: IncCommsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📢 Incident Comms</h3>
        <span className="text-xs text-gray-400">{total} messages</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {messages.map((m, i) => (
          <div key={i} className="px-4 py-2.5">
            <div className="flex items-center gap-2 text-xs mb-0.5">
              <span>{TYPE_ICONS[m.type] ?? "📨"}</span>
              <span className="font-medium capitalize">{m.type}</span>
              <span className="text-gray-400">→ {m.channels.join(", ")}</span>
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-300">{m.message}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";
export function FleetAiDlqPanel({ queues, active, messages, retried, discarded }: { queues: number; active: number; messages: number; retried: number; discarded: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📭 AI Dead Letter Queue</h3>
    <div className="text-sm">{active}/{queues} active · {messages} messages · {retried} retried · {discarded} discarded</div>
  </div>);
}

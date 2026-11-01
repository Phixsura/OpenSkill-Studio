"use client";
export function FleetAiModelAlogPanel({ loggers, active, accesses, users, models }: { loggers: number; active: number; accesses: number; users: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Model Access Log</h3>
    <div className="text-sm">{active}/{loggers} active · {accesses.toLocaleString()} accesses · {users.toLocaleString()} users · {models} models</div>
  </div>);
}

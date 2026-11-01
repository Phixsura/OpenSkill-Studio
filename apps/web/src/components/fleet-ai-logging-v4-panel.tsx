"use client";
export function FleetAiLoggingV4Panel({ systems, active, logs, storage, retention }: { systems: number; active: number; logs: number; storage: number; retention: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Logging v4</h3>
    <div className="text-sm">{active}/{systems} active · {logs.toLocaleString()} logs · {storage}TB · {retention}d retention</div>
  </div>);
}

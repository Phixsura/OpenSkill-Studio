"use client";

interface ScopeCheckerDisplayProps { allowed: boolean; required: string;
  granted: string[]; effective: string[]; reason: string; }

export function ScopeCheckerDisplay({ allowed, required, granted, effective, reason }: ScopeCheckerDisplayProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔑 Scope Check</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${allowed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {allowed ? "✅ Allowed" : "❌ Denied"}
        </span>
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between"><span className="text-gray-400">Required</span>
          <span className="font-mono font-bold">{required}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Granted</span>
          <span className="font-mono">{granted.join(", ")}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Effective</span>
          <div className="flex gap-1">{effective.map(s => (
            <span key={s} className={`text-xs px-1.5 py-0.5 rounded ${s === required ? "bg-blue-100 text-blue-700 font-bold" : "bg-gray-100 dark:bg-gray-800"}`}>{s}</span>
          ))}</div>
        </div>
      </div>
    </div>
  );
}

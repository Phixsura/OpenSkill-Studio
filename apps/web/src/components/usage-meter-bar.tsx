"use client";

interface UsageMeter { label: string; pct: number; status: string; display: string; remainingDisplay: string; }
interface UsageMeterBarProps { meters: UsageMeter[]; }

const STATUS_COLOR: Record<string, string> = { ok: "bg-green-500", warning: "bg-yellow-500", critical: "bg-red-500" };

export function UsageMeterBar({ meters }: UsageMeterBarProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📊 Usage</h3>
      <div className="space-y-3">
        {meters.map(m => (
          <div key={m.label}>
            <div className="flex justify-between text-sm mb-1">
              <span>{m.label}</span>
              <span className="text-xs text-gray-400">{m.display}</span>
            </div>
            <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${STATUS_COLOR[m.status] || "bg-gray-400"}`}
                   style={{ width: `${Math.min(m.pct, 100)}%` }} />
            </div>
            <p className="text-xs text-gray-400 mt-0.5">{m.remainingDisplay} remaining</p>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

interface ServiceLevel { service: string; level: string; overridden: boolean; }
interface LogLevelPanelProps { services: ServiceLevel[]; defaultLevel: string; overriddenCount: number; }

const LEVEL_COLOR: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-500", warn: "text-yellow-600", error: "text-red-500", fatal: "text-red-700",
};

export function LogLevelPanel({ services, defaultLevel, overriddenCount }: LogLevelPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Log Levels</h3>
        <span className="text-xs text-gray-400">default: {defaultLevel} · {overriddenCount} overrides</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <div className="flex items-center gap-2">
              <span className={`font-bold uppercase ${LEVEL_COLOR[s.level] ?? ""}`}>{s.level}</span>
              {s.overridden && <span className="text-[10px] text-yellow-600">override</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

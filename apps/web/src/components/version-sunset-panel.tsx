"use client";
interface VersionInfo { version: string; status: string; daysLeft?: number; }
interface VersionSunsetPanelProps { versions: VersionInfo[]; active: number; sunsetting: number; sunset: number; }
const DOT: Record<string, string> = { active: "bg-green-500", sunsetting: "bg-yellow-500", sunset: "bg-red-500" };
export function VersionSunsetPanel({ versions, active, sunsetting, sunset }: VersionSunsetPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌅 Version Sunsets</h3>
        <span className="text-xs text-gray-400">{active} active · {sunsetting} sunsetting · {sunset} sunset</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {versions.map(v => (
          <div key={v.version} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${DOT[v.status] ?? "bg-gray-400"}`} />
              <span className="font-mono">{v.version}</span>
            </div>
            <span className="text-gray-400">{v.status}{v.daysLeft != null ? ` · ${v.daysLeft}d` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

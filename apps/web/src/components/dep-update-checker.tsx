"use client";

interface OutdatedDep { name: string; current: string; latest: string; type: string; breaking: boolean; }
interface DepUpdateCheckerProps { outdated: OutdatedDep[]; upToDate: number;
  total: number; hasMajor: boolean; onUpdate: (name: string) => void; }

const TYPE_COLORS: Record<string, string> = {
  major: "bg-red-100 text-red-700", minor: "bg-yellow-100 text-yellow-700",
  patch: "bg-green-100 text-green-700",
};

export function DepUpdateChecker({ outdated, upToDate, total, hasMajor, onUpdate }: DepUpdateCheckerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Dependency Updates</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{upToDate} current</span>
          <span className="text-yellow-600">{outdated.length} outdated</span>
          {hasMajor && <span className="text-red-500">⚠ breaking</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {outdated.map(d => (
          <div key={d.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-medium">{d.name}</span>
                <span className={`px-1.5 py-0.5 text-[10px] rounded ${TYPE_COLORS[d.type] ?? ""}`}>{d.type}</span>
              </div>
              <div className="text-[10px] text-gray-400 font-mono">{d.current} → {d.latest}</div>
            </div>
            <button onClick={() => onUpdate(d.name)} className="px-2 py-1 text-xs bg-blue-500 text-white rounded">Update</button>
          </div>
        ))}
      </div>
    </div>
  );
}

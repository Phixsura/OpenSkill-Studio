"use client";

interface FeatureStatus { name: string; priority: number; active: boolean; }
interface GracefulDegradePanelProps { level: string; features: FeatureStatus[];
  active: number; shed: number; }

const LEVEL_STYLE: Record<string, string> = {
  full: "text-green-600", reduced: "text-yellow-600", minimal: "text-orange-500", emergency: "text-red-600",
};

export function GracefulDegradePanel({ level, features, active, shed }: GracefulDegradePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Degradation Level</h3>
        <span className={`text-xs font-bold uppercase ${LEVEL_STYLE[level] ?? ""}`}>
          {level} · {active} active · {shed} shed
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {features.map(f => (
          <div key={f.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${f.active ? "bg-green-500" : "bg-red-500"}`} />
              <span className={f.active ? "" : "line-through text-gray-400"}>{f.name}</span>
            </div>
            <span className="text-gray-400">p{f.priority}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

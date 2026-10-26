"use client";

interface FeatureToggle {
  id: string;
  name: string;
  type: "boolean" | "percentage" | "user_list";
  enabled: boolean;
  percentage: number;
  userCount: number;
  description?: string;
}

const typeLabels: Record<string, string> = {
  boolean: "🔘 Boolean", percentage: "📊 Percentage", user_list: "👥 User List",
};

export function FeatureTogglePanel({
  toggles,
  extensionName,
  onToggle,
  onSetPercentage,
}: {
  toggles: FeatureToggle[];
  extensionName: string;
  onToggle?: (name: string) => void;
  onSetPercentage?: (name: string, pct: number) => void;
}) {
  const enabled = toggles.filter((t) => t.enabled).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚩 {extensionName} Feature Flags</h2>
        <span className="text-sm text-gray-500">{enabled}/{toggles.length} enabled</span>
      </div>

      <div className="space-y-2">
        {toggles.map((toggle) => (
          <div key={toggle.id} className={`rounded-xl border dark:border-gray-700 p-4 ${!toggle.enabled ? "opacity-60" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{toggle.name}</span>
                <span className="text-xs text-gray-400">{typeLabels[toggle.type]}</span>
              </div>
              <button onClick={() => onToggle?.(toggle.name)}
                className={`w-12 h-6 rounded-full relative transition-colors ${toggle.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
                <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow ${toggle.enabled ? "left-6" : "left-0.5"}`} />
              </button>
            </div>
            {toggle.description && <p className="text-xs text-gray-500 mb-2">{toggle.description}</p>}
            {toggle.type === "percentage" && (
              <div className="flex items-center gap-2">
                <input type="range" min={0} max={100} value={toggle.percentage}
                  onChange={(e) => onSetPercentage?.(toggle.name, parseInt(e.target.value))}
                  className="flex-1 h-1.5 accent-blue-600" />
                <span className="text-xs font-mono w-10 text-right">{toggle.percentage}%</span>
              </div>
            )}
            {toggle.type === "user_list" && (
              <span className="text-xs text-gray-500">{toggle.userCount} users targeted</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

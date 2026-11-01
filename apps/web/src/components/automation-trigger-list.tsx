"use client";

interface Trigger { triggerId: string; name: string; eventType: string; enabled: boolean; fireCount: number; }

const typeIcons: Record<string, string> = { schedule: "⏰", webhook: "🔗", event: "⚡", manual: "👆" };

export function AutomationTriggerList({ triggers, onToggle, onFire }: {
  triggers: Trigger[]; onToggle?: (id: string, enabled: boolean) => void; onFire?: (id: string) => void;
}) {
  if (!triggers.length) return <div className="text-center text-gray-400 py-6 text-sm">No triggers configured</div>;
  return (
    <div className="space-y-2">
      {triggers.map(t => (
        <div key={t.triggerId} className={`border dark:border-gray-700 rounded-xl p-3 flex items-center justify-between ${!t.enabled ? "opacity-50" : ""}`}>
          <div className="flex items-center gap-3">
            <span className="text-xl">{typeIcons[t.eventType] || "🔌"}</span>
            <div>
              <span className="font-medium text-sm block">{t.name}</span>
              <span className="text-xs text-gray-500">{t.eventType} · fired {t.fireCount}×</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => onFire?.(t.triggerId)} className="text-xs bg-green-500 text-white px-2 py-1 rounded-lg" disabled={!t.enabled}>Fire</button>
            <button onClick={() => onToggle?.(t.triggerId, !t.enabled)} className={`text-xs px-2 py-1 rounded-lg ${t.enabled ? "bg-gray-200 dark:bg-gray-700" : "bg-blue-500 text-white"}`}>
              {t.enabled ? "Disable" : "Enable"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

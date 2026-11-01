"use client";

interface Rule { name: string; rule_type: string; type_info: { label: string; icon: string };
  channels: string[]; enabled: boolean; }
interface NotificationRuleBuilderProps { rules: Rule[]; onToggle: (name: string) => void;
  onDelete: (name: string) => void; onCreate: () => void; }

export function NotificationRuleBuilder({ rules, onToggle, onDelete, onCreate }: NotificationRuleBuilderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Notification Rules</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">New Rule</button>
      </div>
      {rules.map(r => (
        <div key={r.name} className={`rounded-lg border p-3 ${r.enabled ? "dark:border-gray-700" : "opacity-50 dark:border-gray-800"}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>{r.type_info.icon}</span>
              <span className="font-medium">{r.name}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">{r.type_info.label}</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => onToggle(r.name)} className={`relative h-5 w-9 rounded-full ${r.enabled ? "bg-blue-600" : "bg-gray-300"}`}>
                <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow ${r.enabled ? "left-[1.1rem]" : "left-0.5"}`} />
              </button>
              <button onClick={() => onDelete(r.name)} className="text-xs text-red-400">×</button>
            </div>
          </div>
          <div className="mt-1 flex gap-1">
            {r.channels.map(ch => (
              <span key={ch} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-600 dark:bg-blue-900/20">{ch}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

"use client";

interface FlagChange { audit_id: string; flag_name: string; old_value: boolean; new_value: boolean;
  changed_by: string; reason: string; timestamp: string; change_type: string; }
interface FeatureFlagAuditLogProps { entries: FlagChange[]; total: number; }

const changeIcon: Record<string, string> = { enabled: "🟢", disabled: "🔴", unchanged: "⚪" };

export function FeatureFlagAuditLog({ entries, total }: FeatureFlagAuditLogProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Flag Audit Log</h2>
        <span className="text-xs text-gray-400">{total} changes</span>
      </div>
      <div className="space-y-1.5">
        {entries.map(e => (
          <div key={e.audit_id} className="flex items-center gap-3 rounded border px-3 py-2 dark:border-gray-700">
            <span>{changeIcon[e.change_type] ?? "⚪"}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <code className="font-mono text-xs font-bold">{e.flag_name}</code>
                <span className="text-xs text-gray-400">{e.change_type}</span>
              </div>
              <p className="text-xs text-gray-400">{e.changed_by} — {e.reason}</p>
            </div>
            <span className="text-xs text-gray-300">{e.timestamp.slice(0, 10)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

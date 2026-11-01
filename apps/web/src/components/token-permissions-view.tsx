"use client";

interface Permission { id: string; label: string; icon: string; granted: boolean; }
interface TokenPermissionsViewProps { groups: Record<string, Permission[]>;
  granted: number; total: number; hasAdmin: boolean; }

export function TokenPermissionsView({ groups, granted, total, hasAdmin }: TokenPermissionsViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Token Permissions</h3>
        <div className="flex items-center gap-2">
          {hasAdmin && <span className="text-xs text-red-600">⚠ Admin access</span>}
          <span className="text-xs text-gray-400">{granted}/{total}</span>
        </div>
      </div>
      {Object.entries(groups).map(([group, perms]) => (
        <div key={group}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-1">{group}</p>
          <div className="space-y-1">
            {perms.map(p => (
              <div key={p.id} className="flex items-center gap-2 text-sm">
                <span className={p.granted ? "text-green-600" : "text-gray-300"}>{p.granted ? "✓" : "✗"}</span>
                <span>{p.icon}</span>
                <span className={!p.granted ? "text-gray-400" : ""}>{p.label}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

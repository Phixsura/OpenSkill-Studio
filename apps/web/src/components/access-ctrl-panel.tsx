"use client";

interface RoleInfo { role: string; permissions: string[]; userCount: number; }
interface AccessCtrlPanelProps { roles: RoleInfo[]; totalUsers: number; totalPermissions: number; }

export function AccessCtrlPanel({ roles, totalUsers, totalPermissions }: AccessCtrlPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Access Control</h3>
        <span className="text-xs text-gray-400">{roles.length} roles · {totalUsers} users · {totalPermissions} perms</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {roles.map(r => (
          <div key={r.role} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-bold">{r.role}</span>
              <span className="text-gray-400">{r.userCount} users</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {r.permissions.map(p => (
                <span key={p} className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">{p}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

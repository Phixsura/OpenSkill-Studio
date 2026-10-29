"use client";

interface RoleInfo { role_id: string; name: string; permission_count: number; member_count: number; }
interface Props { roles: RoleInfo[]; appName: string; }

export default function APIDeveloperRoleCard({ roles, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👤 Developer Roles</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{roles.length} roles</span>
      </div>
      {roles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No roles defined</p>
      ) : (
        <div className="space-y-1">
          {roles.map((r) => (
            <div key={r.role_id} className="flex items-center justify-between text-[11px]">
              <span className="font-medium text-gray-700 dark:text-gray-300">{r.name}</span>
              <span className="text-gray-400">{r.permission_count} perms · {r.member_count} members</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

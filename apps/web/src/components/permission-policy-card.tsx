"use client";

interface RoleInfo {
  role_id: string;
  name: string;
  permissions: { resource: string; action: string }[];
}

interface PermissionPolicyCardProps {
  roles: RoleInfo[];
  appName: string;
}

export default function PermissionPolicyCard({ roles, appName }: PermissionPolicyCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔐 Permission Policy
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{roles.length} roles</span>
      </div>

      {roles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No roles defined</p>
      ) : (
        <div className="space-y-2">
          {roles.map((r) => (
            <div
              key={r.role_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {r.name}
                </span>
                <span className="text-[11px] text-gray-400">{r.permissions.length} perms</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {r.permissions.slice(0, 5).map((p) => (
                  <span
                    key={`${p.resource}:${p.action}`}
                    className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {p.resource}:{p.action}
                  </span>
                ))}
                {r.permissions.length > 5 && (
                  <span className="text-[9px] text-gray-400">+{r.permissions.length - 5}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

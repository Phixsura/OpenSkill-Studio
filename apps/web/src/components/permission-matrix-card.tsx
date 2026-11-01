"use client";

interface PermissionInfo {
  resource: string;
  action: string;
  source: "direct" | "wildcard" | "inherited";
}

interface RoleInfo {
  role_id: string;
  name: string;
  inherits_from: string | null;
  permissions: PermissionInfo[];
}

interface PermissionMatrixCardProps {
  roles: RoleInfo[];
  appName: string;
}

const SOURCE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  direct: {
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
    label: "Direct",
  },
  wildcard: {
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
    label: "Wildcard",
  },
  inherited: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-600 dark:text-gray-400",
    label: "Inherited",
  },
};

function PermBadge({ perm }: { perm: PermissionInfo }) {
  const src = SOURCE_STYLES[perm.source] ?? SOURCE_STYLES.direct;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium ${src.bg} ${src.text}`}
    >
      {perm.resource}:{perm.action}
      {perm.source !== "direct" && <span className="opacity-70">({src.label})</span>}
    </span>
  );
}

export default function PermissionMatrixCard({ roles, appName }: PermissionMatrixCardProps) {
  const totalPerms = roles.reduce((s, r) => s + r.permissions.length, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Permission Matrix
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {roles.length} role{roles.length !== 1 ? "s" : ""} · {totalPerms} permission
          {totalPerms !== 1 ? "s" : ""}
        </span>
      </div>

      {roles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No roles configured</p>
      ) : (
        <div className="space-y-3">
          {roles.map((role) => (
            <div
              key={role.role_id}
              className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {role.name}
                </span>
                <span className="font-mono text-[10px] text-gray-400">{role.role_id}</span>
                {role.inherits_from && (
                  <span className="text-[11px] text-gray-400">← {role.inherits_from}</span>
                )}
              </div>
              {role.permissions.length > 0 ? (
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {role.permissions.map((p, i) => (
                    <PermBadge key={`${p.resource}:${p.action}-${i}`} perm={p} />
                  ))}
                </div>
              ) : (
                <p className="mt-1 text-[11px] text-gray-400">No permissions</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

interface RoleInfo { role: string; level: number; permissionCount: number; }
interface RoleSelectorProps { roles: RoleInfo[]; currentRole: string;
  onSelect: (role: string) => void; canAssign: (role: string) => boolean; }

export function RoleSelector({ roles, currentRole, onSelect, canAssign }: RoleSelectorProps) {
  return (
    <div className="space-y-1">
      {roles.map(r => (
        <button key={r.role} onClick={() => canAssign(r.role) && onSelect(r.role)}
          disabled={!canAssign(r.role) && r.role !== currentRole}
          className={`w-full text-left flex items-center justify-between px-3 py-2 rounded-lg text-sm ${
            r.role === currentRole ? "bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-300 font-medium" :
            canAssign(r.role) ? "hover:bg-gray-50 dark:hover:bg-gray-800" : "opacity-40 cursor-not-allowed"
          }`}>
          <span className="capitalize">{r.role}</span>
          <span className="text-xs text-gray-400">{r.permissionCount} permissions</span>
        </button>
      ))}
    </div>
  );
}

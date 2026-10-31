"use client";

import { useState } from "react";

interface PolicyRule {
  resource: string;
  actions: string[];
  decision: "allow" | "deny";
}

interface Role {
  name: string;
  ruleCount: number;
  inherits: string[];
}

interface UserAssignment {
  userId: string;
  role: string;
}

export function AccessPolicyPanel({
  roles,
  assignments,
  selectedRoleRules,
  onSelectRole,
  onAssign,
}: {
  roles: Role[];
  assignments: UserAssignment[];
  selectedRoleRules: PolicyRule[] | null;
  onSelectRole?: (roleName: string) => void;
  onAssign?: (userId: string, role: string) => void;
}) {
  const [tab, setTab] = useState<"roles" | "assignments">("roles");
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🛡️ Access Policies</h2>

      <div className="flex gap-1">
        <button onClick={() => setTab("roles")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "roles" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Roles ({roles.length})
        </button>
        <button onClick={() => setTab("assignments")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "assignments" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Assignments ({assignments.length})
        </button>
      </div>

      {tab === "roles" && (
        <div className="space-y-2">
          {roles.map((role) => (
            <div key={role.name} className="rounded-xl border dark:border-gray-700 overflow-hidden">
              <div className="flex items-center justify-between p-3 cursor-pointer"
                onClick={() => { setSelectedRole(selectedRole === role.name ? null : role.name); onSelectRole?.(role.name); }}>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">{role.name}</span>
                  <span className="text-xs text-gray-400">{role.ruleCount} rules</span>
                  {role.inherits.length > 0 && (
                    <span className="text-xs text-purple-500">← {role.inherits.join(", ")}</span>
                  )}
                </div>
              </div>
              {selectedRole === role.name && selectedRoleRules && (
                <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-1">
                  {selectedRoleRules.map((rule, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <span className={`px-1.5 py-0.5 rounded ${rule.decision === "allow" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                        {rule.decision}
                      </span>
                      <code>{rule.resource}</code>
                      <span className="text-gray-400">[{rule.actions.join(", ")}]</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "assignments" && (
        <div className="space-y-1">
          {assignments.map((a) => (
            <div key={a.userId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
              <span>👤 {a.userId}</span>
              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-2 py-0.5 rounded-full">{a.role}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

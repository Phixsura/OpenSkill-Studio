"use client";

interface PolicyInfo { name: string; effect: string; actions: string[]; conditions: string; }
interface PermPolicyViewerProps { policies: PolicyInfo[]; userPermissions: string[]; }

export function PermPolicyViewer({ policies, userPermissions }: PermPolicyViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Permission Policies</h3>
        <span className="text-xs text-gray-400">{policies.length} policies · {userPermissions.length} perms</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={p.name} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-semibold">{p.name}</span>
              <span className={p.effect === "allow" ? "text-green-600" : "text-red-500"}>{p.effect}</span>
            </div>
            <div className="text-gray-400">{p.actions.join(", ")} · {p.conditions}</div>
          </div>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 p-3 flex flex-wrap gap-1">
        {userPermissions.map(p => (
          <span key={p} className="px-1.5 py-0.5 rounded bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-[10px]">{p}</span>
        ))}
      </div>
    </div>
  );
}

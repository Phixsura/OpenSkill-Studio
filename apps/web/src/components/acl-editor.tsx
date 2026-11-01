"use client";

interface AclRule { resource: string; principal: string; permissions: string[]; }

const permIcons: Record<string, string> = { read: "👁️", write: "✏️", delete: "🗑️", admin: "👑", execute: "▶️" };

export function AclEditor({ rules, onRevoke }: { rules: AclRule[]; onRevoke?: (resource: string, principal: string) => void }) {
  if (!rules.length) return <div className="text-center text-gray-400 py-6 text-sm">No access rules configured</div>;
  return (
    <div className="space-y-2">
      <h3 className="font-bold text-sm">Access Control</h3>
      {rules.map((r, i) => (
        <div key={i} className="border dark:border-gray-700 rounded-xl p-3 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{r.resource}</span>
              <span className="text-xs text-gray-500">→</span>
              <span className="text-xs font-medium">{r.principal}</span>
            </div>
            <div className="flex gap-1 mt-1">
              {r.permissions.map(p => (
                <span key={p} className="text-xs bg-blue-50 dark:bg-blue-900/10 text-blue-600 px-1.5 py-0.5 rounded">
                  {permIcons[p] || ""} {p}
                </span>
              ))}
            </div>
          </div>
          <button onClick={() => onRevoke?.(r.resource, r.principal)} className="text-xs text-red-400 hover:text-red-600">Revoke</button>
        </div>
      ))}
    </div>
  );
}

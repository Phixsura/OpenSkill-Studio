"use client";

interface AppGrant { appId: string; appName: string; scopes: string[]; grantedAt: number; }

const scopeDescriptions: Record<string, string> = {
  "read:profile": "Read your profile", "write:profile": "Edit your profile",
  "read:data": "Access your data", "write:data": "Modify your data",
  "read:analytics": "View analytics", "admin:settings": "Admin settings",
  "webhook:manage": "Manage webhooks", "sandbox:execute": "Run sandboxes",
  "connector:manage": "Manage connectors", "marketplace:publish": "Publish extensions",
};

export function AppPermissionsPanel({ grants, onRevoke }: { grants: AppGrant[]; onRevoke?: (appId: string, scope?: string) => void }) {
  if (!grants.length) return <div className="text-center text-gray-400 py-6 text-sm">No apps have permissions</div>;
  return (
    <div className="space-y-3">
      {grants.map(g => (
        <div key={g.appId} className="border dark:border-gray-700 rounded-xl p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="font-bold text-sm">{g.appName}</span>
            <button onClick={() => onRevoke?.(g.appId)} className="text-xs text-red-500 hover:text-red-700">Revoke All</button>
          </div>
          <div className="flex flex-wrap gap-1">
            {g.scopes.map(s => (
              <span key={s} className="inline-flex items-center gap-1 text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                {scopeDescriptions[s] || s}
                <button onClick={() => onRevoke?.(g.appId, s)} className="text-gray-400 hover:text-red-500">×</button>
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

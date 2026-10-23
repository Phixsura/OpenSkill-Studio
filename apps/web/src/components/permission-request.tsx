"use client";

interface Permission { id: string; label: string; description: string; risk: string; icon: string; }
interface PermissionRequestProps { permissions: Permission[]; maxRisk: string;
  requiresAdmin: boolean; onAllow: () => void; onDeny: () => void; appName: string; }

const riskColors: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-red-600",
};

export function PermissionRequest({ permissions, maxRisk, requiresAdmin, onAllow, onDeny, appName }: PermissionRequestProps) {
  return (
    <div className="mx-auto max-w-md space-y-4">
      <div className="text-center">
        <h2 className="text-lg font-bold">{appName} requests access</h2>
        {requiresAdmin && <p className="text-xs text-red-600 mt-1">⚠ Requires admin approval</p>}
      </div>
      <div className="space-y-2">
        {permissions.map(p => (
          <div key={p.id} className="flex items-start gap-3 rounded-lg border p-3 dark:border-gray-700">
            <span className="text-lg mt-0.5">{p.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{p.label}</p>
              <p className="text-xs text-gray-400">{p.description}</p>
            </div>
            <span className={`text-xs ${riskColors[p.risk] ?? ""}`}>{p.risk}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-3">
        <button onClick={onDeny} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Deny</button>
        <button onClick={onAllow}
          className={`flex-1 rounded py-2 text-sm text-white ${maxRisk === "high" ? "bg-red-600" : "bg-blue-600"}`}>Allow</button>
      </div>
    </div>
  );
}

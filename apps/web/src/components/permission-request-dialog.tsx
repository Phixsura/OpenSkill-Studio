"use client";

interface PermDetail { permission: string; label: string; risk: string; granted: boolean; }
interface PermissionRequestDialogProps { appName: string; details: PermDetail[];
  maxRisk: string; onApprove: () => void; onDeny: () => void; }

const RISK_STYLE: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function PermissionRequestDialog({ appName, details, maxRisk, onApprove, onDeny }: PermissionRequestDialogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 max-w-md shadow-xl bg-white dark:bg-gray-900">
      <h3 className="font-bold mb-1">{appName} requests access</h3>
      <p className="text-xs text-gray-400 mb-4">Review the permissions below</p>
      <div className="space-y-2 mb-4">
        {details.map(d => (
          <div key={d.permission} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-2">
            <span>{d.label}</span>
            <span className={`text-xs font-medium ${RISK_STYLE[d.risk] || ""}`}>{d.risk}</span>
          </div>
        ))}
      </div>
      {maxRisk === "critical" && (
        <p className="text-xs text-red-500 mb-3">⚠️ This app requests critical-level permissions</p>
      )}
      <div className="flex gap-2">
        <button onClick={onDeny} className="flex-1 py-2 border rounded text-sm hover:bg-gray-50 dark:hover:bg-gray-800">Deny</button>
        <button onClick={onApprove} className="flex-1 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Approve</button>
      </div>
    </div>
  );
}

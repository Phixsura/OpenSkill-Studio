"use client";

interface Permission { name: string; risk: string; description?: string; }
interface InstallConfirmationDialogProps { appName: string; permissions: Permission[];
  priceLabel: string; maxRisk: string; requiresReview: boolean; confirmMessage: string;
  onConfirm: () => void; onCancel: () => void; }

const riskDot: Record<string, string> = { low: "bg-green-500", medium: "bg-yellow-500", high: "bg-orange-500", critical: "bg-red-500" };

export function InstallConfirmationDialog({ appName, permissions, priceLabel, maxRisk,
  requiresReview, confirmMessage, onConfirm, onCancel }: InstallConfirmationDialogProps) {
  return (
    <div className="mx-auto max-w-md rounded-xl border bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <div className="text-center">
        <span className="text-4xl">📥</span>
        <h2 className="mt-2 text-xl font-bold">Install {appName}</h2>
        <p className="mt-1 text-sm text-gray-500">{confirmMessage}</p>
      </div>
      {permissions.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-400">Permissions ({permissions.length})</h3>
          <div className="mt-2 space-y-1.5">
            {permissions.map(p => (
              <div key={p.name} className="flex items-center gap-2 text-sm">
                <span className={`h-2 w-2 rounded-full ${riskDot[p.risk] ?? riskDot.low}`} />
                <span>{p.name}</span>
                <span className="text-xs text-gray-400">({p.risk})</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="mt-5 flex gap-2">
        <button onClick={onCancel} className="flex-1 rounded-lg border py-2.5 text-sm dark:border-gray-600">Cancel</button>
        <button onClick={onConfirm}
          className={`flex-1 rounded-lg py-2.5 text-sm font-semibold text-white ${requiresReview ? "bg-orange-600" : "bg-blue-600"}`}>
          {priceLabel === "Free" ? "Install" : `Install — ${priceLabel}`}
        </button>
      </div>
    </div>
  );
}

"use client";

interface UpgradePlanCardProps { targetVersion: string; total: number; autoUpgrade: number; manualUpgrade: number; needsConsent: boolean; newPermissions: string[]; onExecute?: () => void; }

export function UpgradePlanCard({ targetVersion, total, autoUpgrade, manualUpgrade, needsConsent, newPermissions, onExecute }: UpgradePlanCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">Upgrade to v{targetVersion}</h4>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-sm">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-500">Total</p></div>
        <div><p className="text-lg font-bold text-green-600">{autoUpgrade}</p><p className="text-xs text-gray-500">Auto</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{manualUpgrade}</p><p className="text-xs text-gray-500">Manual</p></div>
      </div>
      {needsConsent && <p className="mb-2 text-xs text-yellow-600">⚠️ New permissions: {newPermissions.join(", ")}</p>}
      {onExecute && <button onClick={onExecute} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Execute Upgrade</button>}
    </div>
  );
}

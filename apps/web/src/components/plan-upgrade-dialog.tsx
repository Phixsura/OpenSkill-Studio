"use client";

interface PlanUpgradeDialogProps { currentPlan: string; targetPlan: string;
  isUpgrade: boolean; priceDiffDisplay: string; newPrice: number;
  warning: string | null; onConfirm: () => void; onCancel: () => void; }

export function PlanUpgradeDialog({ currentPlan, targetPlan, isUpgrade, priceDiffDisplay,
  newPrice, warning, onConfirm, onCancel }: PlanUpgradeDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-sm rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700">
        <h2 className="text-lg font-bold">{isUpgrade ? "⬆️ Upgrade" : "⬇️ Downgrade"} Plan</h2>
        <p className="mt-2 text-sm text-gray-500">
          <span className="capitalize">{currentPlan}</span> → <span className="capitalize font-bold">{targetPlan}</span>
        </p>
        <div className="mt-3 rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-2xl font-bold">${newPrice}/mo</p>
          <p className="text-xs text-gray-400">{priceDiffDisplay}</p>
        </div>
        {warning && <p className="mt-2 text-xs text-yellow-600">⚠ {warning}</p>}
        <div className="mt-4 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Cancel</button>
          <button onClick={onConfirm}
            className={`flex-1 rounded py-2 text-sm text-white ${isUpgrade ? "bg-blue-600" : "bg-yellow-600"}`}>
            {isUpgrade ? "Upgrade Now" : "Downgrade"}
          </button>
        </div>
      </div>
    </div>
  );
}

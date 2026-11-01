"use client";

interface DataItem { category: string; count: number; label: string; }
interface AccountDeletionPageProps { items: DataItem[]; totalRecords: number;
  scheduledDeletion: string; gracePeriodDays: number; canCancel: boolean;
  onConfirm: () => void; onCancel: () => void; }

export function AccountDeletionPage({ items, totalRecords, scheduledDeletion,
  gracePeriodDays, canCancel, onConfirm, onCancel }: AccountDeletionPageProps) {
  return (
    <div className="mx-auto max-w-lg space-y-5">
      <div className="rounded-xl border-2 border-red-300 p-5 dark:border-red-700">
        <h2 className="text-lg font-bold text-red-600">⚠ Delete Account</h2>
        <p className="mt-2 text-sm text-gray-500">
          Your account and all data will be permanently deleted on{" "}
          <strong>{new Date(scheduledDeletion).toLocaleDateString()}</strong>{" "}
          ({gracePeriodDays}-day grace period).
        </p>
      </div>
      <div className="space-y-2">
        <h3 className="text-sm font-semibold">Data to be deleted ({totalRecords} records)</h3>
        {items.map(i => (
          <div key={i.category} className="flex items-center justify-between rounded border px-4 py-2 dark:border-gray-700">
            <span className="text-sm">{i.label}</span>
            <span className="text-xs text-gray-400">{i.count} records</span>
          </div>
        ))}
      </div>
      <div className="flex gap-3">
        {canCancel && <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Keep Account</button>}
        <button onClick={onConfirm} className="flex-1 rounded bg-red-600 py-2 text-sm text-white">Delete Everything</button>
      </div>
    </div>
  );
}

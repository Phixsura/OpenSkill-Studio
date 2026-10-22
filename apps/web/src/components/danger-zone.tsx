"use client";

interface DangerZoneProps { canDelete: boolean; canArchive: boolean; onDelete?: () => void; onArchive?: () => void; }

export function DangerZone({ canDelete, canArchive, onDelete, onArchive }: DangerZoneProps) {
  if (!canDelete && !canArchive) return null;
  return (
    <div className="rounded-lg border border-red-200 p-4 dark:border-red-800">
      <h4 className="mb-3 font-semibold text-red-700 dark:text-red-300">⚠️ Danger Zone</h4>
      <div className="space-y-2">
        {canArchive && onArchive && <button onClick={onArchive} className="w-full rounded border border-yellow-500 px-4 py-2 text-sm text-yellow-700 hover:bg-yellow-50">Archive App</button>}
        {canDelete && onDelete && <button onClick={onDelete} className="w-full rounded border border-red-500 px-4 py-2 text-sm text-red-700 hover:bg-red-50">Delete App</button>}
      </div>
    </div>
  );
}

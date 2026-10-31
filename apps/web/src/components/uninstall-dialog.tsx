"use client";

interface DataItem { type: string; label: string; sizeKb: number; }
interface UninstallDialogProps { appName: string; dataToRemove: DataItem[];
  totalSizeDisplay: string; warning: string;
  onConfirm: () => void; onCancel: () => void; }

export function UninstallDialog({ appName, dataToRemove, totalSizeDisplay, warning, onConfirm, onCancel }: UninstallDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700">
        <h2 className="text-lg font-bold text-red-600">🗑️ Uninstall {appName}</h2>
        <p className="mt-2 text-sm text-gray-500">{warning}</p>
        <div className="mt-3 space-y-1">
          <p className="text-xs font-semibold text-gray-400">Data to remove ({totalSizeDisplay})</p>
          {dataToRemove.map(d => (
            <div key={d.type} className="flex items-center justify-between text-sm">
              <span>{d.label}</span>
              <span className="text-xs text-gray-400">{d.sizeKb}KB</span>
            </div>
          ))}
        </div>
        <div className="mt-4 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Keep App</button>
          <button onClick={onConfirm} className="flex-1 rounded bg-red-600 py-2 text-sm text-white">Uninstall</button>
        </div>
      </div>
    </div>
  );
}

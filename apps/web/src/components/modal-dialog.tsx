"use client";

interface ModalDialogProps { title: string; sizeClass: string; closable: boolean;
  hasFooter: boolean; danger: boolean; children: React.ReactNode;
  onClose: () => void; onConfirm?: () => void; confirmLabel?: string; }

export function ModalDialog({ title, sizeClass, closable, hasFooter, danger,
  children, onClose, onConfirm, confirmLabel = "Confirm" }: ModalDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={closable ? onClose : undefined}>
      <div className={`w-full ${sizeClass} rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700`}
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className={`text-lg font-bold ${danger ? "text-red-600" : ""}`}>{title}</h2>
          {closable && <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>}
        </div>
        <div>{children}</div>
        {hasFooter && (
          <div className="mt-4 flex justify-end gap-2">
            <button onClick={onClose} className="rounded border px-4 py-2 text-sm dark:border-gray-700">Cancel</button>
            {onConfirm && (
              <button onClick={onConfirm}
                className={`rounded px-4 py-2 text-sm text-white ${danger ? "bg-red-600" : "bg-blue-600"}`}>{confirmLabel}</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

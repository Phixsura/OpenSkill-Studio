"use client";

interface ModalContainerProps { title: string; sizeClass: string; dismissible: boolean;
  hasFooter: boolean; onClose: () => void; onConfirm?: () => void;
  children: React.ReactNode; }

export function ModalContainer({ title, sizeClass, dismissible, hasFooter,
  onClose, onConfirm, children }: ModalContainerProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={dismissible ? onClose : undefined}>
      <div className={`${sizeClass} w-full rounded-xl bg-white shadow-2xl dark:bg-gray-900`}
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b px-5 py-3 dark:border-gray-700">
          <h2 className="text-lg font-semibold">{title}</h2>
          {dismissible && <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>}
        </div>
        <div className="p-5">{children}</div>
        {hasFooter && (
          <div className="flex justify-end gap-2 border-t px-5 py-3 dark:border-gray-700">
            <button onClick={onClose} className="rounded border px-4 py-1.5 text-sm dark:border-gray-600">Cancel</button>
            {onConfirm && (
              <button onClick={onConfirm} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Confirm</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

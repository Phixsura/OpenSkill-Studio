"use client";

interface ModalShellProps { title: string; size: string; closable: boolean;
  hasFooter: boolean; children: React.ReactNode;
  onClose: () => void; onConfirm?: () => void; }

const SIZE_CLASS: Record<string, string> = {
  sm: "max-w-sm", md: "max-w-lg", lg: "max-w-2xl", xl: "max-w-4xl", full: "max-w-full",
};

export function ModalShell({ title, size, closable, hasFooter, children, onClose, onConfirm }: ModalShellProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full ${SIZE_CLASS[size] || SIZE_CLASS.md} mx-4`}>
        <div className="flex items-center justify-between px-5 py-3 border-b dark:border-gray-700">
          <h3 className="font-semibold">{title}</h3>
          {closable && <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>}
        </div>
        <div className="px-5 py-4 max-h-[60vh] overflow-y-auto">{children}</div>
        {hasFooter && (
          <div className="flex justify-end gap-2 px-5 py-3 border-t dark:border-gray-700">
            <button onClick={onClose} className="px-4 py-1.5 text-sm border rounded hover:bg-gray-50">Cancel</button>
            {onConfirm && <button onClick={onConfirm} className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">Confirm</button>}
          </div>
        )}
      </div>
    </div>
  );
}

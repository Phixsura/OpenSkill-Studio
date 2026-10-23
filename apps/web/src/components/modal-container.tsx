"use client";

interface ModalContainerProps {
  open: boolean; title: string; sizeClass?: string;
  closeable?: boolean; onClose: () => void; children: React.ReactNode;
}

export function ModalContainer({ open, title, sizeClass = "max-w-md", closeable = true, onClose, children }: ModalContainerProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={closeable ? onClose : undefined}>
      <div className={`w-full ${sizeClass} rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800`} onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">{title}</h2>
          {closeable && <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>}
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}

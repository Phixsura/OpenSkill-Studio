"use client";

interface ConfirmDialogProps {
  title: string; message: string; confirmLabel?: string; cancelLabel?: string;
  destructive?: boolean; onConfirm: () => void; onCancel: () => void;
}

export function ConfirmDialog({ title, message, confirmLabel = "Confirm", cancelLabel = "Cancel", destructive, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{message}</p>
        <div className="mt-4 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded border px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{cancelLabel}</button>
          <button onClick={onConfirm} className={`rounded px-4 py-2 text-sm text-white ${destructive ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}`}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}

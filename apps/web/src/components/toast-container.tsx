"use client";

interface Toast { id: string; title: string; message: string; variant: string;
  icon: string; dismissible: boolean; }
interface ToastContainerProps { toasts: Toast[]; onDismiss: (id: string) => void; }

const VARIANT_STYLE: Record<string, string> = {
  success: "border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800",
  error: "border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800",
  warning: "border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-800",
  info: "border-blue-200 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800",
};

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 w-80">
      {toasts.map(t => (
        <div key={t.id} className={`rounded-lg border p-3 shadow-lg flex items-start gap-2 ${VARIANT_STYLE[t.variant] || ""}`}>
          <span className="text-lg">{t.icon}</span>
          <div className="flex-1">
            <p className="text-sm font-medium">{t.title}</p>
            {t.message && <p className="text-xs text-gray-500">{t.message}</p>}
          </div>
          {t.dismissible && (
            <button onClick={() => onDismiss(t.id)} className="text-xs text-gray-400 hover:text-gray-600">✕</button>
          )}
        </div>
      ))}
    </div>
  );
}

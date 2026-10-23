"use client";

interface Toast { type: string; title: string; message?: string; icon: string; dismissible: boolean; }
interface ToastContainerProps { toasts: Toast[]; onDismiss: (index: number) => void; }

const TYPE_STYLES: Record<string, string> = {
  success: "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/20",
  error: "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/20",
  warning: "border-yellow-300 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-900/20",
  info: "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20",
};

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((t, i) => (
        <div key={i} className={`flex items-start gap-2 rounded-lg border px-4 py-3 shadow-lg ${TYPE_STYLES[t.type] || TYPE_STYLES.info}`}>
          <span>{t.icon}</span>
          <div className="flex-1">
            <p className="text-sm font-semibold">{t.title}</p>
            {t.message && <p className="text-xs opacity-80">{t.message}</p>}
          </div>
          {t.dismissible && <button onClick={() => onDismiss(i)} className="text-xs opacity-50 hover:opacity-100">✕</button>}
        </div>
      ))}
    </div>
  );
}

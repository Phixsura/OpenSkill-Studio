"use client";

interface Toast { id: string; message: string; type: string; icon: string; color: string;
  actionLabel: string | null; dismissible: boolean; }
interface ToastStackProps { toasts: Toast[]; onDismiss: (id: string) => void; onAction: (id: string) => void; }

const bgColors: Record<string, string> = {
  green: "bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800",
  red: "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800",
  yellow: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800",
  blue: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800",
};

export function ToastStack({ toasts, onDismiss, onAction }: ToastStackProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 w-80">
      {toasts.map(t => (
        <div key={t.id} className={`flex items-start gap-2 rounded-lg border p-3 shadow-lg ${bgColors[t.color] ?? bgColors.blue}`}>
          <span>{t.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm">{t.message}</p>
            {t.actionLabel && (
              <button onClick={() => onAction(t.id)} className="mt-1 text-xs font-medium text-blue-600 hover:underline">{t.actionLabel}</button>
            )}
          </div>
          {t.dismissible && (
            <button onClick={() => onDismiss(t.id)} className="text-gray-400 hover:text-gray-600 text-xs">✕</button>
          )}
        </div>
      ))}
    </div>
  );
}

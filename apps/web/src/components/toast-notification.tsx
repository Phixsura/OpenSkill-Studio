"use client";

interface ToastNotificationProps { message: string; type: string; icon: string;
  actionLabel: string | null; onAction?: () => void; onDismiss: () => void; }

const typeStyle: Record<string, string> = {
  success: "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/10",
  error: "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/10",
  warning: "border-yellow-300 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-900/10",
  info: "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/10",
};

export function ToastNotification({ message, type, icon, actionLabel, onAction, onDismiss }: ToastNotificationProps) {
  return (
    <div className={`flex items-center gap-3 rounded-lg border p-3 shadow-lg ${typeStyle[type] ?? typeStyle.info}`}>
      <span className="text-lg">{icon}</span>
      <p className="flex-1 text-sm">{message}</p>
      {actionLabel && onAction && (
        <button onClick={onAction} className="text-xs font-medium text-blue-600">{actionLabel}</button>
      )}
      <button onClick={onDismiss} className="text-xs text-gray-400">✕</button>
    </div>
  );
}

"use client";

interface AlertAction { label: string; url: string; }
interface AlertBannerProps { message: string; title: string | null; variant: string;
  icon: string; bgClass: string; dismissible: boolean; action: AlertAction | null;
  onDismiss: () => void; onAction?: () => void; }

export function AlertBanner({ message, title, variant, icon, bgClass, dismissible,
  action, onDismiss, onAction }: AlertBannerProps) {
  return (
    <div className={`flex items-start gap-3 rounded-lg border p-4 ${bgClass}`}>
      <span className="text-lg">{icon}</span>
      <div className="flex-1">
        {title && <h3 className="text-sm font-semibold">{title}</h3>}
        <p className={`text-sm ${title ? "mt-0.5" : ""} text-gray-600 dark:text-gray-300`}>{message}</p>
        {action && onAction && (
          <button onClick={onAction} className="mt-2 text-xs font-medium text-blue-600 hover:underline">
            {action.label} →
          </button>
        )}
      </div>
      {dismissible && (
        <button onClick={onDismiss} className="text-xs text-gray-400 hover:text-gray-600">✕</button>
      )}
    </div>
  );
}

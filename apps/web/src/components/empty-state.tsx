"use client";

interface EmptyStateProps { title: string; message: string; icon: string; action?: string | null; onAction?: () => void; }

export function EmptyState({ title, message, icon, action, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 py-12 dark:border-gray-700">
      <span className="text-4xl">{icon}</span>
      <h3 className="mt-3 text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{message}</p>
      {action && onAction && (
        <button onClick={onAction} className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
          {action}
        </button>
      )}
    </div>
  );
}

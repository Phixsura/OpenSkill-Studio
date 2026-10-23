"use client";

interface Action { label: string; action: string; url?: string; }
interface ErrorBoundaryFallbackProps { title: string; message: string; icon: string;
  actions: Action[]; showStackTrace: boolean; error?: string;
  onAction: (action: string, url?: string) => void; }

export function ErrorBoundaryFallback({ title, message, icon, actions, showStackTrace,
  error, onAction }: ErrorBoundaryFallbackProps) {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="mx-auto max-w-md space-y-4 text-center">
        <span className="text-5xl">{icon}</span>
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="text-sm text-gray-500">{message}</p>
        {showStackTrace && error && (
          <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-3 text-left font-mono text-xs text-red-400">
            {error}
          </pre>
        )}
        <div className="flex justify-center gap-2">
          {actions.map(a => (
            <button key={a.label} onClick={() => onAction(a.action, a.url)}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">
              {a.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

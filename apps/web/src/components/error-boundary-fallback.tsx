"use client";

interface ErrorAction { label: string; action: string; url?: string; }
interface ErrorBoundaryFallbackProps { title: string; message: string;
  actions: ErrorAction[]; showDetails: boolean; stackPreview?: string;
  onAction: (action: string, url?: string) => void; }

export function ErrorBoundaryFallback({ title, message, actions, showDetails, stackPreview, onAction }: ErrorBoundaryFallbackProps) {
  return (
    <div className="min-h-[300px] flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <p className="text-5xl mb-4">💥</p>
        <h2 className="text-xl font-bold mb-2">{title}</h2>
        <p className="text-sm text-gray-500 mb-6">{message}</p>
        <div className="flex gap-2 justify-center mb-4">
          {actions.map(a => (
            <button key={a.label} onClick={() => onAction(a.action, a.url)}
              className={`text-sm px-4 py-2 rounded-lg ${
                a.action === "retry" ? "bg-blue-600 text-white hover:bg-blue-700" :
                "border hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}>{a.label}</button>
          ))}
        </div>
        {showDetails && stackPreview && (
          <pre className="text-xs text-left bg-gray-100 dark:bg-gray-800 rounded-lg p-3 overflow-auto max-h-32 text-gray-500">{stackPreview}</pre>
        )}
      </div>
    </div>
  );
}

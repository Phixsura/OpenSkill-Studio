"use client";

interface ErrorAction { label: string; action: string; }
interface ErrorPageProps { status: number; title: string; description: string;
  detail: string; requestId: string; actions: ErrorAction[];
  onAction: (action: string) => void; }

const STATUS_EMOJI: Record<number, string> = {
  400: "🚫", 401: "🔒", 403: "⛔", 404: "🔍", 429: "⏳", 500: "💥", 503: "🔧",
};

export function ErrorPage({ status, title, description, detail, requestId, actions, onAction }: ErrorPageProps) {
  return (
    <div className="min-h-[400px] flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <p className="text-6xl mb-4">{STATUS_EMOJI[status] || "❌"}</p>
        <h1 className="text-4xl font-black text-gray-900 dark:text-white mb-2">{status}</h1>
        <h2 className="text-xl font-bold mb-2">{title}</h2>
        <p className="text-sm text-gray-500 mb-4">{description}</p>
        {detail && <p className="text-xs text-gray-400 bg-gray-50 dark:bg-gray-800 rounded p-2 mb-4">{detail}</p>}
        <div className="flex gap-2 justify-center mb-4">
          {actions.map(a => (
            <button key={a.action} onClick={() => onAction(a.action)}
              className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700">{a.label}</button>
          ))}
        </div>
        {requestId && <p className="text-xs text-gray-300">Request ID: {requestId}</p>}
      </div>
    </div>
  );
}

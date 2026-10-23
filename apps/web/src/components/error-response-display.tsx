"use client";

interface ApiError { code: string; message: string; status: number; field?: string; }
interface ErrorResponseDisplayProps { error: ApiError; onRetry?: () => void; onBack?: () => void; }

const statusIcons: Record<number, string> = {
  400: "🚫", 401: "🔒", 403: "⛔", 404: "🔍", 409: "💥", 422: "⚠️", 429: "🐢", 500: "💣",
};

export function ErrorResponseDisplay({ error, onRetry, onBack }: ErrorResponseDisplayProps) {
  return (
    <div className="mx-auto max-w-md space-y-4 rounded-lg border border-red-200 p-6 text-center dark:border-red-800">
      <span className="text-4xl">{statusIcons[error.status] ?? "❌"}</span>
      <div>
        <p className="text-lg font-bold">{error.status}</p>
        <p className="text-sm font-medium text-red-600">{error.code}</p>
      </div>
      <p className="text-sm text-gray-500">{error.message}</p>
      {error.field && <p className="font-mono text-xs text-gray-400">Field: {error.field}</p>}
      <div className="flex justify-center gap-2">
        {onRetry && <button onClick={onRetry} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Retry</button>}
        {onBack && <button onClick={onBack} className="rounded border px-4 py-1.5 text-sm dark:border-gray-600">Go Back</button>}
      </div>
    </div>
  );
}

"use client";

interface FullErrorPageProps { statusCode: number; title: string; icon: string;
  message: string; suggestions: string[]; onGoHome: () => void; onGoBack: () => void; }

export function FullErrorPage({ statusCode, title, icon, message, suggestions, onGoHome, onGoBack }: FullErrorPageProps) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="mx-auto max-w-md space-y-6 text-center">
        <span className="text-6xl">{icon}</span>
        <div>
          <p className="text-5xl font-black text-gray-200 dark:text-gray-700">{statusCode}</p>
          <h1 className="mt-2 text-2xl font-bold">{title}</h1>
          <p className="mt-2 text-sm text-gray-500">{message}</p>
        </div>
        {suggestions.length > 0 && (
          <div className="rounded-lg bg-gray-50 p-4 text-left dark:bg-gray-800">
            <p className="text-xs font-medium text-gray-400">Try this:</p>
            <ul className="mt-1 space-y-1">
              {suggestions.map((s, i) => (
                <li key={i} className="flex items-center gap-1.5 text-sm text-gray-500">
                  <span className="text-blue-500">→</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="flex justify-center gap-3">
          <button onClick={onGoBack} className="rounded border px-4 py-2 text-sm dark:border-gray-600">Go Back</button>
          <button onClick={onGoHome} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Home</button>
        </div>
      </div>
    </div>
  );
}

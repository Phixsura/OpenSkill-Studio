"use client";

interface ErrorPageViewProps { statusCode: number; title: string; icon: string;
  description: string; suggestions: string[]; requestId: string | null; }

export function ErrorPageView({ statusCode, title, icon, description, suggestions, requestId }: ErrorPageViewProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center text-center p-8">
      <span className="text-6xl mb-4">{icon}</span>
      <h1 className="text-4xl font-bold text-gray-900 dark:text-white">{statusCode}</h1>
      <h2 className="mt-2 text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-gray-500 max-w-md">{description}</p>
      {suggestions.length > 0 && (
        <div className="mt-6 space-y-2">
          <p className="text-sm font-medium text-gray-400">Try these:</p>
          {suggestions.map((s, i) => (
            <p key={i} className="text-sm text-blue-600">→ {s}</p>
          ))}
        </div>
      )}
      {requestId && <p className="mt-4 text-xs text-gray-400">Request ID: {requestId}</p>}
    </div>
  );
}

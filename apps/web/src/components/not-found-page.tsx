"use client";

interface NotFoundPageProps { requestedPath: string; suggestions: string[];
  categoryMatches: string[]; }

export function NotFoundPage({ requestedPath, suggestions, categoryMatches }: NotFoundPageProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center text-center p-8">
      <span className="text-6xl mb-4">🔍</span>
      <h1 className="text-4xl font-bold">404</h1>
      <p className="mt-2 text-gray-500">Page not found: <code className="text-sm">{requestedPath}</code></p>
      {suggestions.length > 0 && (
        <div className="mt-6">
          <p className="text-sm font-medium text-gray-400 mb-2">Did you mean?</p>
          <div className="space-y-1">
            {suggestions.map(s => (
              <a key={s} href={s} className="block text-sm text-blue-600 hover:underline">{s}</a>
            ))}
          </div>
        </div>
      )}
      {categoryMatches.length > 0 && suggestions.length === 0 && (
        <div className="mt-6">
          <p className="text-sm font-medium text-gray-400 mb-2">Related pages</p>
          {categoryMatches.map(p => (
            <a key={p} href={p} className="block text-sm text-blue-600 hover:underline">{p}</a>
          ))}
        </div>
      )}
    </div>
  );
}

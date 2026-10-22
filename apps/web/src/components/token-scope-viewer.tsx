"use client";

interface TokenScopeViewerProps { name: string; grantedScopes: string[]; effectiveScopes: string[]; }

export function TokenScopeViewer({ name, grantedScopes, effectiveScopes }: TokenScopeViewerProps) {
  const inherited = effectiveScopes.filter(s => !grantedScopes.includes(s));
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">{name}</h3>
      <div className="mt-3 space-y-2">
        <div>
          <p className="text-xs font-medium text-gray-500">Granted</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {grantedScopes.map(s => (
              <span key={s} className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">{s}</span>
            ))}
          </div>
        </div>
        {inherited.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500">Inherited</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {inherited.map(s => (
                <span key={s} className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-700">{s}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

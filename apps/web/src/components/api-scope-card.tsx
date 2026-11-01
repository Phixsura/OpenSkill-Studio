"use client";

interface ScopeInfo {
  scope_id: string;
  name: string;
  description: string;
  category: string;
}

interface APIScopeCardProps {
  scopes: ScopeInfo[];
  appName: string;
}

export default function APIScopeCard({ scopes, appName }: APIScopeCardProps) {
  const categories = [...new Set(scopes.map((s) => s.category))];

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔓 API Scopes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {scopes.length} scopes · {categories.length} categories
        </span>
      </div>

      {scopes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scopes defined</p>
      ) : (
        <div className="space-y-1.5">
          {scopes.map((s) => (
            <div
              key={s.scope_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {s.scope_id}
                </span>
              </div>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                {s.category}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

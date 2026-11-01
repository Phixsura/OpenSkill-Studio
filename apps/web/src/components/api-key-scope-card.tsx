"use client";

interface ScopedKeyInfo {
  key_id: string;
  prefix: string;
  scopes: string[];
  label: string;
  active: boolean;
  request_count: number;
}

interface APIKeyScopeCardProps {
  keys: ScopedKeyInfo[];
  appName: string;
}

export default function APIKeyScopeCard({ keys, appName }: APIKeyScopeCardProps) {
  const active = keys.filter((k) => k.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔐 Scoped API Keys
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active}/{keys.length} active
        </span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scoped keys</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div
              key={k.key_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!k.active ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] text-gray-600 dark:text-gray-400">
                    {k.prefix}...
                  </span>
                  {k.label && <span className="text-[11px] text-gray-500">{k.label}</span>}
                </div>
                <span className="text-[10px] text-gray-400">{k.request_count} reqs</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {k.scopes.map((s) => (
                  <span
                    key={s}
                    className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

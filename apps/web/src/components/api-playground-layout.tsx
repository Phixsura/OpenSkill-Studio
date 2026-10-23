"use client";

interface Collection { name: string; }
interface Environment { name: string; }
interface ApiPlaygroundLayoutProps { collections: Collection[]; environments: Environment[];
  activeEnv: string; onEnvChange: (name: string) => void; children: React.ReactNode; }

export function ApiPlaygroundLayout({ collections, environments, activeEnv, onEnvChange, children }: ApiPlaygroundLayoutProps) {
  return (
    <div className="flex h-full gap-4">
      <div className="w-48 space-y-4">
        <div>
          <h3 className="text-xs font-semibold text-gray-400">Environment</h3>
          <select value={activeEnv} onChange={e => onEnvChange(e.target.value)}
            className="mt-1 w-full rounded border p-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
            {environments.map(e => <option key={e.name} value={e.name}>{e.name}</option>)}
          </select>
        </div>
        <div>
          <h3 className="text-xs font-semibold text-gray-400">Collections</h3>
          <ul className="mt-1 space-y-0.5">
            {collections.map(c => (
              <li key={c.name} className="rounded px-2 py-1 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
                {c.name}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="flex-1">{children}</div>
    </div>
  );
}

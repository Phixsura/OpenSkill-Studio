"use client";

interface App { id: string; name: string; icon: string; version: string;
  status: string; installs: number; rating: number; }
interface AppListPageProps { apps: App[]; total: number; sortBy: string;
  hasDraft: boolean; onSort: (sort: string) => void; onSelect: (id: string) => void;
  onCreate: () => void; }

const statusBadge: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30",
  draft: "bg-gray-100 text-gray-500 dark:bg-gray-800",
  review: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
};

export function AppListPage({ apps, total, sortBy, hasDraft, onSort, onSelect, onCreate }: AppListPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 My Apps ({total})</h2>
        <div className="flex items-center gap-2">
          <select value={sortBy} onChange={e => onSort(e.target.value)}
            className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
            <option value="newest">Newest</option><option value="installs">Most Installs</option>
            <option value="name">Name</option>
          </select>
          <button onClick={onCreate} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">+ Create App</button>
        </div>
      </div>
      <div className="space-y-2">
        {apps.map(a => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left hover:shadow dark:border-gray-700">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{a.icon}</span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">{a.name}</span>
                  <span className="text-xs text-gray-400">v{a.version}</span>
                  <span className={`rounded px-1.5 py-0.5 text-xs ${statusBadge[a.status] ?? ""}`}>{a.status}</span>
                </div>
                <p className="text-xs text-gray-400">⭐ {a.rating} · {a.installs.toLocaleString()} installs</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

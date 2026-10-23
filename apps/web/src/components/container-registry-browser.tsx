"use client";

interface RepoInfo { name: string; visibility: string; tagCount: number; pulls: number; }
interface ContainerRegistryBrowserProps { repos: RepoInfo[]; onSelect: (name: string) => void; }

export function ContainerRegistryBrowser({ repos, onSelect }: ContainerRegistryBrowserProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🐳 Container Registry</h3>
      <div className="space-y-2">
        {repos.map(r => (
          <button key={r.name} onClick={() => onSelect(r.name)}
            className="w-full flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            <div>
              <p className="text-sm font-mono font-medium">{r.name}</p>
              <div className="flex gap-3 mt-0.5 text-xs text-gray-400">
                <span>{r.tagCount} tags</span>
                <span>{r.pulls.toLocaleString()} pulls</span>
              </div>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              r.visibility === "public" ? "bg-green-100 text-green-700" : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
            }`}>{r.visibility}</span>
          </button>
        ))}
        {repos.length === 0 && <p className="text-sm text-gray-400">No repositories</p>}
      </div>
    </div>
  );
}

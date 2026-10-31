"use client";

interface SvcInfo { type: string; team: string; language: string; status: string; }
interface Connection { from: string; to: string; }
interface SvcMapExplorerProps { services: Record<string, SvcInfo>; connections: Connection[];
  teams: string[]; languages: string[]; serviceCount: number; }

export function SvcMapExplorer({ services, connections, teams, languages, serviceCount }: SvcMapExplorerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Service Map</h3>
        <span className="text-xs text-gray-400">{serviceCount} services · {connections.length} connections · {teams.length} teams</span>
      </div>
      <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-2">
        {Object.entries(services).map(([name, info]) => (
          <div key={name} className={`rounded-lg border p-2 text-center ${info.status === "healthy" ? "border-green-300 dark:border-green-800" : "border-red-300 dark:border-red-800"}`}>
            <div className="text-xs font-mono font-bold">{name}</div>
            <div className="text-[10px] text-gray-400">{info.team} · {info.language}</div>
          </div>
        ))}
      </div>
      <div className="px-4 py-2 border-t dark:border-gray-700 text-[10px] text-gray-400">
        Languages: {languages.join(", ")}
      </div>
    </div>
  );
}

"use client";

interface PlaygroundEnv { id: string; owner: string; template: string; status: string;
  resources: { cpu: string; memory: string; storage: string }; }
interface PlaygroundEnvListProps { envs: PlaygroundEnv[]; running: number;
  onCreate: () => void; onStop: (id: string) => void; }

const STATUS_BADGE: Record<string, string> = {
  running: "bg-green-100 text-green-700", stopped: "bg-gray-200 text-gray-600",
  expired: "bg-red-100 text-red-600",
};

export function PlaygroundEnvList({ envs, running, onCreate, onStop }: PlaygroundEnvListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 Playgrounds</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{running} running</span>
          <button onClick={onCreate} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ New</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {envs.map(e => (
          <div key={e.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="text-sm font-mono">{e.id}</div>
              <div className="text-[10px] text-gray-400">{e.template} · {e.resources.cpu} · {e.resources.memory}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_BADGE[e.status] ?? ""}`}>{e.status}</span>
              {e.status === "running" && (
                <button onClick={() => onStop(e.id)} className="text-xs text-red-500">Stop</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

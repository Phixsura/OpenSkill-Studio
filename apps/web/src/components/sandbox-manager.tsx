"use client";

interface SandboxInfo { id: string; name: string; baseUrl: string; status: string; requestCount: number; }
interface SandboxManagerProps { sandboxes: SandboxInfo[];
  onCreate: () => void; onDestroy: (id: string) => void; }

export function SandboxManager({ sandboxes, onCreate, onDestroy }: SandboxManagerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🏖️ Sandboxes</h3>
        <button onClick={onCreate}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">+ New Sandbox</button>
      </div>
      <div className="space-y-2">
        {sandboxes.map(s => (
          <div key={s.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm font-medium">{s.name}</p>
              <p className="text-xs font-mono text-gray-400">{s.baseUrl}</p>
              <p className="text-xs text-gray-400">{s.requestCount} requests</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded">{s.status}</span>
              <button onClick={() => onDestroy(s.id)}
                className="text-xs px-2 py-1 text-red-500 hover:text-red-700">Delete</button>
            </div>
          </div>
        ))}
        {sandboxes.length === 0 && <p className="text-sm text-gray-400 text-center">No sandboxes</p>}
      </div>
    </div>
  );
}

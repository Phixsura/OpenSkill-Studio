"use client";

interface MeshPolicy { name: string; source: string; destination: string;
  timeoutMs: number; retries: number; circuitBreaker: boolean; }
interface MeshPolicyEditorProps { policies: MeshPolicy[]; cbCoveragePct: number;
  onAdd: () => void; }

export function MeshPolicyEditor({ policies, cbCoveragePct, onAdd }: MeshPolicyEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Policies</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{policies.length} policies · {cbCoveragePct}% CB</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={p.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{p.source} → {p.destination}</span>
              <span className="text-gray-400 ml-2">{p.timeoutMs}ms · {p.retries} retries</span>
            </div>
            {p.circuitBreaker && <span className="text-blue-500 text-[10px]">⚡ CB</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

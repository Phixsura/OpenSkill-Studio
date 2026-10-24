"use client";

interface Runtime { id: string; label: string; icon: string; }
interface SandboxConfigProps { runtimes: Runtime[]; selectedRuntime: string;
  memoryMb: number; timeoutS: number; onSelect: (id: string) => void; }

export function SandboxConfig({ runtimes, selectedRuntime, memoryMb, timeoutS, onSelect }: SandboxConfigProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Sandbox Configuration</h3>
      <div className="grid grid-cols-3 gap-2">
        {runtimes.map(r => (
          <button key={r.id} onClick={() => onSelect(r.id)}
            className={`rounded-lg border p-3 text-center transition ${selectedRuntime === r.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <span className="text-lg">{r.icon}</span>
            <p className="mt-1 text-xs font-medium">{r.label}</p>
          </button>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{memoryMb}MB</p>
          <p className="text-xs text-gray-400">Memory</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{timeoutS}s</p>
          <p className="text-xs text-gray-400">Timeout</p>
        </div>
      </div>
    </div>
  );
}

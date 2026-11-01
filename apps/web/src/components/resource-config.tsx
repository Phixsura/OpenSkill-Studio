"use client";

interface Preset { id: string; cpuM: number; memoryMb: number; replicas: number; monthlyCostUsd: number; }
interface ResourceConfigProps { presets: Preset[]; selected: string; onSelect: (id: string) => void; }

export function ResourceConfig({ presets, selected, onSelect }: ResourceConfigProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Resources</h3>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {presets.map(p => (
          <button key={p.id} onClick={() => onSelect(p.id)}
            className={`rounded-lg border p-3 text-left transition ${selected === p.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
            <p className="text-sm font-semibold capitalize">{p.id}</p>
            <div className="mt-1 text-xs text-gray-400 space-y-0.5">
              <p>{p.cpuM}m CPU · {p.memoryMb}MB RAM</p>
              <p>{p.replicas} replica{p.replicas > 1 ? "s" : ""}</p>
              <p className="font-medium text-gray-600 dark:text-gray-300">${p.monthlyCostUsd}/mo</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

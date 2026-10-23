"use client";

interface Preset { id: string; name: string; timeout: number; memory: number; network: boolean; }

const PRESETS: Preset[] = [
  { id: "minimal", name: "Minimal", timeout: 2000, memory: 64, network: false },
  { id: "default", name: "Default", timeout: 5000, memory: 128, network: true },
  { id: "full", name: "Full Power", timeout: 30000, memory: 512, network: true },
];

interface PlaygroundPresetSelectorProps { selected: string; onSelect: (id: string) => void; }

export function PlaygroundPresetSelector({ selected, onSelect }: PlaygroundPresetSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Environment Preset</label>
      <div className="grid grid-cols-3 gap-2">
        {PRESETS.map(p => (
          <button key={p.id} onClick={() => onSelect(p.id)}
            className={`rounded-lg border p-3 text-left text-sm transition ${selected === p.id ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"}`}>
            <p className="font-semibold">{p.name}</p>
            <p className="mt-1 text-xs text-gray-500">{p.memory}MB · {p.timeout / 1000}s timeout</p>
            <p className="text-xs text-gray-400">{p.network ? "🌐 Network" : "🔒 Isolated"}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

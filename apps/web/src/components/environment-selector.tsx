"use client";

interface EnvOption { id: string; label: string; icon: string; protected: boolean; }
interface EnvironmentSelectorProps { environments: EnvOption[]; selected: string;
  onSelect: (id: string) => void; }

export function EnvironmentSelector({ environments, selected, onSelect }: EnvironmentSelectorProps) {
  return (
    <div className="flex gap-2">
      {environments.map(e => (
        <button key={e.id} onClick={() => onSelect(e.id)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm border-2 transition ${
            e.id === selected ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" :
            "border-transparent bg-gray-50 dark:bg-gray-800 hover:border-gray-200"
          }`}>
          <span>{e.icon}</span>
          <span className={e.id === selected ? "font-medium" : "text-gray-500"}>{e.label}</span>
          {e.protected && <span className="text-xs text-yellow-500">🔒</span>}
        </button>
      ))}
    </div>
  );
}

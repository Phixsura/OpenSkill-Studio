"use client";

interface Environment { id: string; label: string; icon: string; color: string; protected: boolean; active: boolean; }
interface EnvironmentSwitcherProps { environments: Environment[]; current: string;
  onSwitch: (id: string) => void; }

export function EnvironmentSwitcher({ environments, current, onSwitch }: EnvironmentSwitcherProps) {
  return (
    <div className="flex items-center gap-1 rounded-lg border p-1 dark:border-gray-700">
      {environments.map(env => (
        <button key={env.id} onClick={() => onSwitch(env.id)}
          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm ${env.active ? "bg-blue-600 text-white" : "text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"}`}>
          <span>{env.icon}</span>
          <span>{env.label}</span>
          {env.protected && <span className="text-[10px]">🔒</span>}
        </button>
      ))}
    </div>
  );
}

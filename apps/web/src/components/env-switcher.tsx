"use client";

interface EnvInfo { id: string; label: string; icon: string; color: string; url: string; }
interface EnvSwitcherProps { environments: EnvInfo[]; current: string;
  onSwitch: (envId: string) => void; }

const COLOR_CLASS: Record<string, string> = {
  blue: "border-blue-500", yellow: "border-yellow-500", green: "border-green-500",
};

export function EnvSwitcher({ environments, current, onSwitch }: EnvSwitcherProps) {
  return (
    <div className="flex gap-2">
      {environments.map(e => (
        <button key={e.id} onClick={() => onSwitch(e.id)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm border-2 transition ${
            e.id === current ? `${COLOR_CLASS[e.color] || ""} bg-white dark:bg-gray-900` :
            "border-transparent hover:bg-gray-50 dark:hover:bg-gray-800"
          }`}>
          <span>{e.icon}</span>
          <span className={e.id === current ? "font-medium" : "text-gray-500"}>{e.label}</span>
        </button>
      ))}
    </div>
  );
}

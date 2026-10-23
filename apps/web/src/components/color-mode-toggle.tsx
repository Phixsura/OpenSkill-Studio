"use client";

interface ColorModeToggleProps { currentMode: string; onModeChange: (mode: string) => void; }

const modes = [
  { id: "light", icon: "☀️", label: "Light" },
  { id: "dark", icon: "🌙", label: "Dark" },
  { id: "system", icon: "💻", label: "System" },
];

export function ColorModeToggle({ currentMode, onModeChange }: ColorModeToggleProps) {
  return (
    <div className="flex items-center gap-1 rounded-lg border p-1 dark:border-gray-700">
      {modes.map(m => (
        <button key={m.id} onClick={() => onModeChange(m.id)} title={m.label}
          className={`rounded-md px-2.5 py-1.5 text-sm ${currentMode === m.id ? "bg-blue-600 text-white" : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"}`}>
          {m.icon}
        </button>
      ))}
    </div>
  );
}

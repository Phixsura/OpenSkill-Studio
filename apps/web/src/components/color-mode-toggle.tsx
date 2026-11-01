"use client";

interface ColorModeToggleProps { current: string; onSelect: (mode: string) => void; }

const MODES = [
  { id: "light", icon: "☀️", label: "Light" },
  { id: "dark", icon: "🌙", label: "Dark" },
  { id: "system", icon: "💻", label: "System" },
];

export function ColorModeToggle({ current, onSelect }: ColorModeToggleProps) {
  return (
    <div className="inline-flex rounded-lg border dark:border-gray-700 p-0.5">
      {MODES.map(m => (
        <button key={m.id} onClick={() => onSelect(m.id)}
          className={`px-3 py-1.5 text-xs rounded-md transition ${
            m.id === current ? "bg-blue-600 text-white" : "text-gray-500 hover:text-gray-700"
          }`} title={m.label}>{m.icon}</button>
      ))}
    </div>
  );
}

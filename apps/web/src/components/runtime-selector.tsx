"use client";

const RUNTIMES = [
  { value: "python3.12", label: "Python 3.12", icon: "🐍" },
  { value: "python3.11", label: "Python 3.11", icon: "🐍" },
  { value: "nodejs20", label: "Node.js 20", icon: "🟢" },
  { value: "nodejs22", label: "Node.js 22", icon: "🟢" },
];

interface RuntimeSelectorProps {
  selected: string;
  onChange: (runtime: string) => void;
}

export function RuntimeSelector({ selected, onChange }: RuntimeSelectorProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {RUNTIMES.map(r => (
        <button key={r.value} onClick={() => onChange(r.value)}
          className={`rounded-lg border px-3 py-2 text-sm ${
            selected === r.value ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"
          }`}>
          {r.icon} {r.label}
        </button>
      ))}
    </div>
  );
}

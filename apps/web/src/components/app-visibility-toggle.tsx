"use client";

interface AppVisibilityToggleProps {
  visibility: "private" | "public" | "unlisted";
  onChange: (visibility: "private" | "public" | "unlisted") => void;
}

const OPTIONS = [
  { value: "private" as const, icon: "🔒", label: "Private", desc: "Only you can see" },
  { value: "unlisted" as const, icon: "🔗", label: "Unlisted", desc: "Accessible via link" },
  { value: "public" as const, icon: "🌍", label: "Public", desc: "Listed in marketplace" },
];

export function AppVisibilityToggle({ visibility, onChange }: AppVisibilityToggleProps) {
  return (
    <div className="flex gap-2">
      {OPTIONS.map(opt => (
        <button key={opt.value} onClick={() => onChange(opt.value)}
          className={`flex-1 rounded-lg border p-3 text-center text-sm transition-colors ${
            visibility === opt.value
              ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/20"
              : "border-gray-200 hover:border-gray-300 dark:border-gray-700"
          }`}>
          <span className="text-xl">{opt.icon}</span>
          <p className="mt-1 font-medium">{opt.label}</p>
          <p className="text-xs text-gray-500">{opt.desc}</p>
        </button>
      ))}
    </div>
  );
}

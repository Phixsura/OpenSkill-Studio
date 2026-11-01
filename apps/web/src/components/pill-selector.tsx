"use client";

interface Pill { id: string; label: string; icon: string | null; selected: boolean; disabled: boolean; }
interface PillSelectorProps { pills: Pill[]; selectedCount: number; maxSelect: number | null;
  onToggle: (id: string) => void; }

export function PillSelector({ pills, selectedCount, maxSelect, onToggle }: PillSelectorProps) {
  return (
    <div className="space-y-2">
      {maxSelect && (
        <p className="text-xs text-gray-400">Select up to {maxSelect} ({selectedCount}/{maxSelect})</p>
      )}
      <div className="flex flex-wrap gap-2">
        {pills.map(p => (
          <button key={p.id} onClick={() => !p.disabled && onToggle(p.id)}
            disabled={p.disabled}
            className={`rounded-full border px-3 py-1.5 text-sm transition-colors disabled:opacity-40 ${
              p.selected
                ? "border-blue-500 bg-blue-50 font-medium text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                : "border-gray-200 hover:border-blue-300 dark:border-gray-600"}`}>
            {p.icon && <span className="mr-1">{p.icon}</span>}
            {p.label}
            {p.selected && <span className="ml-1 text-xs">✕</span>}
          </button>
        ))}
      </div>
    </div>
  );
}

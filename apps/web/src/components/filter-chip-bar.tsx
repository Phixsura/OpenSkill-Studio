"use client";

interface FilterChip { key: string; value: string; label: string; icon: string; }
interface FilterChipBarProps { chips: FilterChip[]; onRemove: (key: string, value: string) => void;
  onClearAll: () => void; }

export function FilterChipBar({ chips, onRemove, onClearAll }: FilterChipBarProps) {
  if (chips.length === 0) return null;
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400">Filters:</span>
      <div className="flex flex-wrap gap-1">
        {chips.map((c, i) => (
          <span key={`${c.key}-${c.value}-${i}`}
            className="flex items-center gap-1 rounded-full border bg-white px-2.5 py-0.5 text-xs dark:border-gray-600 dark:bg-gray-800">
            <span>{c.icon}</span>
            <span>{c.label}</span>
            <button onClick={() => onRemove(c.key, c.value)} className="text-gray-400 hover:text-red-500">×</button>
          </span>
        ))}
      </div>
      <button onClick={onClearAll} className="text-xs text-blue-500">Clear all</button>
    </div>
  );
}

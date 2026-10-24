"use client";

interface CategoryChip { id: string; label: string; icon: string; active: boolean; count: number | null; }
interface CategoryChipBarProps { chips: CategoryChip[]; onSelect: (id: string) => void; }

export function CategoryChipBar({ chips, onSelect }: CategoryChipBarProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {chips.map(chip => (
        <button key={chip.id} onClick={() => onSelect(chip.id)}
          className={`flex flex-shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors ${
            chip.active
              ? "border-blue-500 bg-blue-50 font-medium text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
              : "border-gray-200 text-gray-500 hover:border-blue-300 dark:border-gray-600"}`}>
          <span>{chip.icon}</span>
          <span>{chip.label}</span>
          {chip.count !== null && (
            <span className="rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">{chip.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}

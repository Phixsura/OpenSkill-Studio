"use client";

interface ActiveFilter { key: string; display: string; }
interface SearchFilterBarProps { filters: ActiveFilter[]; activeCount: number;
  onRemove: (key: string) => void; onClear: () => void; }

export function SearchFilterBar({ filters, activeCount, onRemove, onClear }: SearchFilterBarProps) {
  if (activeCount === 0) return null;
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-xs text-gray-400">{activeCount} filters:</span>
      {filters.map(f => (
        <span key={f.key} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400">
          {f.display}
          <button onClick={() => onRemove(f.key)} className="hover:text-red-500">×</button>
        </span>
      ))}
      <button onClick={onClear} className="text-xs text-gray-400 hover:text-red-500">Clear all</button>
    </div>
  );
}

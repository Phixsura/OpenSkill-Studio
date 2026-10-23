"use client";

interface SortOption { id: string; label: string; icon: string; }
interface ViewMode { id: string; label: string; icon: string; }
interface AppGalleryToolbarProps {
  sortOptions: SortOption[]; viewModes: ViewMode[];
  activeSort: string; activeView: string; totalResults: number;
  onSortChange: (id: string) => void; onViewChange: (id: string) => void;
}

export function AppGalleryToolbar({ sortOptions, viewModes, activeSort, activeView, totalResults, onSortChange, onViewChange }: AppGalleryToolbarProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-2 dark:border-gray-700">
      <span className="text-sm text-gray-500">{totalResults.toLocaleString()} apps</span>
      <div className="flex items-center gap-3">
        <select value={activeSort} onChange={e => onSortChange(e.target.value)}
          className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700">
          {sortOptions.map(o => <option key={o.id} value={o.id}>{o.icon} {o.label}</option>)}
        </select>
        <div className="flex gap-1">
          {viewModes.map(m => (
            <button key={m.id} onClick={() => onViewChange(m.id)}
              className={`rounded px-2 py-1 text-sm ${activeView === m.id ? "bg-blue-100 text-blue-700" : "text-gray-400"}`}>
              {m.icon}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

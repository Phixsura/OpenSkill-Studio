"use client";

interface SelectedApp { id: string; name: string; icon: string; }
interface ComparePickerBarProps { selected: SelectedApp[]; canCompare: boolean;
  canAdd: boolean; maxCompare: number;
  onRemove: (id: string) => void; onCompare: () => void; }

export function ComparePickerBar({ selected, canCompare, canAdd, maxCompare, onRemove, onCompare }: ComparePickerBarProps) {
  if (!selected.length) return null;
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-white dark:bg-gray-900 border dark:border-gray-700 rounded-xl shadow-2xl px-4 py-3 flex items-center gap-3 z-50">
      <span className="text-xs text-gray-400">Compare ({selected.length}/{maxCompare}):</span>
      {selected.map(a => (
        <span key={a.id} className="inline-flex items-center gap-1 text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
          {a.icon} {a.name}
          <button onClick={() => onRemove(a.id)} className="text-gray-400 hover:text-red-500">×</button>
        </span>
      ))}
      <button onClick={onCompare} disabled={!canCompare}
        className="text-xs px-4 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
        Compare
      </button>
    </div>
  );
}

"use client";

interface Facet { value: string; count: number; }
interface SearchFiltersProps { facets: Record<string, Facet[]>; activeFilters: Record<string, string>;
  onFilter: (field: string, value: string) => void; onClear: () => void; }

export function SearchFilters({ facets, activeFilters, onFilter, onClear }: SearchFiltersProps) {
  const activeCount = Object.keys(activeFilters).length;
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Filters</h3>
        {activeCount > 0 && (
          <button onClick={onClear} className="text-xs text-blue-600 hover:underline">Clear ({activeCount})</button>
        )}
      </div>
      {Object.entries(facets).map(([field, values]) => (
        <div key={field}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-1">{field}</p>
          <div className="space-y-0.5">
            {values.map(v => (
              <button key={v.value} onClick={() => onFilter(field, v.value)}
                className={`flex w-full items-center justify-between rounded px-2 py-1 text-sm ${activeFilters[field] === v.value ? "bg-blue-50 text-blue-700 dark:bg-blue-900/10" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
                <span>{v.value}</span>
                <span className="text-xs text-gray-400">{v.count}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

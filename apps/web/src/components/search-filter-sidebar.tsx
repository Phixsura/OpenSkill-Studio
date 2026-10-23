"use client";

interface FilterDef { label: string; type: string; options?: string[]; }
interface SearchFilterSidebarProps { filters: Record<string, FilterDef>; activeFilters: Record<string, string>; onFilter: (key: string, value: string) => void; onClear: () => void; }

export function SearchFilterSidebar({ filters, activeFilters, onFilter, onClear }: SearchFilterSidebarProps) {
  const activeCount = Object.keys(activeFilters).length;
  return (
    <div className="w-56 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        {activeCount > 0 && <button onClick={onClear} className="text-xs text-blue-600">Clear ({activeCount})</button>}
      </div>
      <div className="mt-3 space-y-4">
        {Object.entries(filters).map(([key, def]) => (
          <div key={key}>
            <label className="block text-xs font-medium text-gray-500">{def.label}</label>
            {def.type === "select" && def.options && (
              <select value={activeFilters[key] || ""} onChange={e => onFilter(key, e.target.value)}
                className="mt-1 w-full rounded border p-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
                <option value="">All</option>
                {def.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            )}
            {def.type === "boolean" && (
              <label className="mt-1 flex items-center gap-1 text-sm">
                <input type="checkbox" checked={activeFilters[key] === "true"} onChange={e => onFilter(key, e.target.checked ? "true" : "")} />
                {def.label}
              </label>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

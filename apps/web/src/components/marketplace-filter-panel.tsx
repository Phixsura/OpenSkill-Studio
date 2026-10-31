"use client";

interface FilterPanelProps {
  categories: string[]; selectedCategory: string; onCategoryChange: (c: string) => void;
  verifiedOnly: boolean; onVerifiedChange: (v: boolean) => void;
  minHealth: number; onMinHealthChange: (h: number) => void;
}

export function MarketplaceFilterPanel({ categories, selectedCategory, onCategoryChange, verifiedOnly, onVerifiedChange, minHealth, onMinHealthChange }: FilterPanelProps) {
  return (
    <div className="space-y-4 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="font-semibold">Filters</h4>
      <div>
        <label className="text-xs text-gray-500">Category</label>
        <select value={selectedCategory} onChange={e => onCategoryChange(e.target.value)} className="mt-1 w-full rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800">
          <option value="">All</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <div>
        <label className="text-xs text-gray-500">Min Health Score: {minHealth}</label>
        <input type="range" min={0} max={100} value={minHealth} onChange={e => onMinHealthChange(Number(e.target.value))} className="w-full" />
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={verifiedOnly} onChange={e => onVerifiedChange(e.target.checked)} />
        Verified developers only
      </label>
    </div>
  );
}

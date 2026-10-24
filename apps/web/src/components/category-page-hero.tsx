"use client";

interface Subcategory { id: string; name: string; }
interface CategoryPageHeroProps { name: string; icon: string; description: string; appCount: number; subcategories: Subcategory[]; onSubcategoryClick: (id: string) => void; }

export function CategoryPageHero({ name, icon, description, appCount, subcategories, onSubcategoryClick }: CategoryPageHeroProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 p-6 dark:from-blue-900/10 dark:to-indigo-900/10">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{icon}</span>
        <div>
          <h1 className="text-2xl font-bold">{name}</h1>
          <p className="text-sm text-gray-500">{description}</p>
          <p className="mt-1 text-xs text-gray-400">{appCount} apps</p>
        </div>
      </div>
      {subcategories.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {subcategories.map(s => (
            <button key={s.id} onClick={() => onSubcategoryClick(s.id)}
              className="rounded-full border border-gray-200 px-3 py-1 text-sm hover:bg-white dark:border-gray-700 dark:hover:bg-gray-800">
              {s.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

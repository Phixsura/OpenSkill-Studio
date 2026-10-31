"use client";

interface Category { categoryId: string; name: string; icon: string; extensionCount: number; children?: Category[]; }

export function CategorySidebar({ categories, selected, onSelect }: {
  categories: Category[]; selected: string; onSelect?: (id: string) => void;
}) {
  return (
    <nav className="space-y-0.5">
      <button onClick={() => onSelect?.("")}
        className={`w-full text-left px-3 py-2 rounded-lg text-sm ${!selected ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 font-medium" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
        📋 All Categories
      </button>
      {categories.map(c => (
        <div key={c.categoryId}>
          <button onClick={() => onSelect?.(c.categoryId)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm flex justify-between ${selected === c.categoryId ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 font-medium" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
            <span>{c.icon} {c.name}</span>
            {c.extensionCount > 0 && <span className="text-xs text-gray-400">{c.extensionCount}</span>}
          </button>
          {c.children?.map(child => (
            <button key={child.categoryId} onClick={() => onSelect?.(child.categoryId)}
              className={`w-full text-left pl-8 pr-3 py-1.5 rounded-lg text-xs ${selected === child.categoryId ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
              {child.name}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}

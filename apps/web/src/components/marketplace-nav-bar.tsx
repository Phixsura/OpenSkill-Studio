"use client";

interface NavItem { id: string; label: string; url: string; icon: string; active: boolean; badge?: string | null; }
interface MarketplaceNavBarProps { items: NavItem[]; onNavigate: (url: string) => void; }

export function MarketplaceNavBar({ items, onNavigate }: MarketplaceNavBarProps) {
  return (
    <nav className="flex items-center gap-1 border-b border-gray-200 px-4 dark:border-gray-700">
      {items.map(item => (
        <button key={item.id} onClick={() => onNavigate(item.url)}
          className={`relative flex items-center gap-1.5 px-3 py-2.5 text-sm transition ${
            item.active ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500 hover:text-gray-700"}`}>
          <span>{item.icon}</span>
          <span>{item.label}</span>
          {item.badge && (
            <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-blue-600 text-xs text-white">
              {item.badge}
            </span>
          )}
        </button>
      ))}
    </nav>
  );
}

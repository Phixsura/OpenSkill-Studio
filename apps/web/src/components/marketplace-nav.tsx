"use client";

interface MarketplaceNavProps { activePage: string; }

const NAV = [
  { key: "home", label: "Home", href: "/marketplace", icon: "🏠" },
  { key: "apps", label: "All Apps", href: "/marketplace/apps", icon: "📦" },
  { key: "categories", label: "Categories", href: "/marketplace/apps/categories", icon: "📂" },
  { key: "featured", label: "Featured", href: "/marketplace/featured", icon: "⭐" },
  { key: "trending", label: "Trending", href: "/marketplace/trending", icon: "🔥" },
  { key: "developers", label: "Developers", href: "/marketplace/developers", icon: "👩‍💻" },
];

export function MarketplaceNav({ activePage }: MarketplaceNavProps) {
  return (
    <nav className="flex gap-1 overflow-x-auto border-b border-gray-200 dark:border-gray-700">
      {NAV.map(n => (
        <a key={n.key} href={n.href}
          className={`whitespace-nowrap px-3 py-2 text-sm ${activePage === n.key ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500 hover:text-gray-700"}`}>
          {n.icon} {n.label}
        </a>
      ))}
    </nav>
  );
}

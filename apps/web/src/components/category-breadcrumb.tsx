"use client";

interface Crumb { key: string; label: string; }
interface CategoryBreadcrumbProps { crumbs: Crumb[]; }

export function CategoryBreadcrumb({ crumbs }: CategoryBreadcrumbProps) {
  return (
    <nav className="flex items-center gap-1 text-sm" aria-label="Category breadcrumb">
      <a href="/marketplace" className="text-gray-400 hover:text-gray-600">Marketplace</a>
      {crumbs.map((c, i) => (
        <span key={c.key} className="flex items-center gap-1">
          <span className="text-gray-300">/</span>
          {i === crumbs.length - 1 ? (
            <span className="font-medium">{c.label}</span>
          ) : (
            <a href={`/marketplace/category/${c.key}`} className="text-gray-400 hover:text-gray-600">{c.label}</a>
          )}
        </span>
      ))}
    </nav>
  );
}

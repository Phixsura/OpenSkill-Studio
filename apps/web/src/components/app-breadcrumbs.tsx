"use client";

interface Crumb { label: string; href?: string; }
interface AppBreadcrumbsProps { crumbs: Crumb[]; }

export function AppBreadcrumbs({ crumbs }: AppBreadcrumbsProps) {
  return (
    <nav className="flex items-center gap-1 text-sm text-gray-500">
      {crumbs.map((c, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span>/</span>}
          {c.href ? <a href={c.href} className="hover:text-blue-600">{c.label}</a> : <span className="text-gray-800 dark:text-gray-200">{c.label}</span>}
        </span>
      ))}
    </nav>
  );
}

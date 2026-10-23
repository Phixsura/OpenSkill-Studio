"use client";

interface Crumb { label: string; url: string | null; active: boolean; }
interface BreadcrumbNavProps { crumbs: Crumb[]; }

export function BreadcrumbNav({ crumbs }: BreadcrumbNavProps) {
  return (
    <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
      {crumbs.map((c, i) => (
        <span key={i} className="flex items-center gap-1.5">
          {i > 0 && <span className="text-gray-300 dark:text-gray-600">/</span>}
          {c.active ? (
            <span className="font-medium text-gray-900 dark:text-gray-100">{c.label}</span>
          ) : (
            <a href={c.url || "#"} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              {c.label}
            </a>
          )}
        </span>
      ))}
    </nav>
  );
}

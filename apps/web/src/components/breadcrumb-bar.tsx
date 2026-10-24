"use client";

interface Crumb { label: string; path: string; active: boolean; }
interface BreadcrumbBarProps { crumbs: Crumb[]; onNavigate: (path: string) => void; }

export function BreadcrumbBar({ crumbs, onNavigate }: BreadcrumbBarProps) {
  return (
    <nav className="flex items-center gap-1 text-sm py-2">
      {crumbs.map((c, i) => (
        <div key={c.path} className="flex items-center gap-1">
          {i > 0 && <span className="text-gray-300">/</span>}
          {c.active ? (
            <span className="font-medium text-gray-900 dark:text-gray-100">{c.label}</span>
          ) : (
            <button onClick={() => onNavigate(c.path)}
              className="text-gray-500 hover:text-blue-600 transition">{c.label}</button>
          )}
        </div>
      ))}
    </nav>
  );
}

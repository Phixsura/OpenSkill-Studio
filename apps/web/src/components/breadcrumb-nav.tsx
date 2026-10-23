"use client";

interface Crumb { label: string; path: string; active: boolean; }
interface BreadcrumbNavProps { breadcrumbs: Crumb[]; onNavigate: (path: string) => void; }

export function BreadcrumbNav({ breadcrumbs, onNavigate }: BreadcrumbNavProps) {
  return (
    <nav className="flex items-center gap-1 text-sm">
      {breadcrumbs.map((crumb, i) => (
        <div key={crumb.path} className="flex items-center gap-1">
          {i > 0 && <span className="text-gray-300 dark:text-gray-600">/</span>}
          {crumb.active ? (
            <span className="font-medium text-gray-800 dark:text-gray-200">{crumb.label}</span>
          ) : (
            <button onClick={() => onNavigate(crumb.path)}
              className="text-gray-400 hover:text-blue-500 hover:underline">
              {crumb.label}
            </button>
          )}
        </div>
      ))}
    </nav>
  );
}

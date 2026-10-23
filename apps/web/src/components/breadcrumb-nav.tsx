"use client";

interface BreadcrumbItem { label: string; href: string | null; is_current: boolean; }
interface BreadcrumbNavProps { trail: BreadcrumbItem[]; }

export function BreadcrumbNav({ trail }: BreadcrumbNavProps) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm">
      {trail.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span className="text-gray-400">/</span>}
          {item.href ? (
            <a href={item.href} className="text-blue-600 hover:underline dark:text-blue-400">{item.label}</a>
          ) : (
            <span className={item.is_current ? "font-medium text-gray-900 dark:text-white" : "text-gray-500"}>{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

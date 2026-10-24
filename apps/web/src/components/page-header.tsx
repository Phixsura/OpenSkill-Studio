"use client";

interface Breadcrumb { label: string; path: string; }
interface Action { label: string; type: string; }
interface PageHeaderProps { title: string; subtitle?: string; breadcrumbs: Breadcrumb[];
  actions: Action[]; onBreadcrumbClick: (path: string) => void; onAction: (label: string) => void; }

export function PageHeader({ title, subtitle, breadcrumbs, actions, onBreadcrumbClick, onAction }: PageHeaderProps) {
  return (
    <div className="space-y-2">
      {breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-1 text-xs text-gray-400">
          {breadcrumbs.map((bc, i) => (
            <span key={bc.path} className="flex items-center gap-1">
              {i > 0 && <span>/</span>}
              <button onClick={() => onBreadcrumbClick(bc.path)} className="hover:text-blue-500">{bc.label}</button>
            </span>
          ))}
        </nav>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          {subtitle && <p className="mt-0.5 text-sm text-gray-400">{subtitle}</p>}
        </div>
        {actions.length > 0 && (
          <div className="flex gap-2">
            {actions.map(a => (
              <button key={a.label} onClick={() => onAction(a.label)}
                className={`rounded-lg px-4 py-2 text-sm font-medium ${a.type === "primary" ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
                {a.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

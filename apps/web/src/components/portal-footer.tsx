"use client";

interface FooterLink { label: string; url: string; }
interface PortalFooterProps { links: Record<string, FooterLink[]>; version: string; copyright: string; }

export function PortalFooter({ links, version, copyright }: PortalFooterProps) {
  return (
    <footer className="mt-12 border-t border-gray-200 pt-8 dark:border-gray-800">
      <div className="grid grid-cols-2 gap-6 sm:grid-cols-3 lg:grid-cols-4">
        {Object.entries(links).map(([section, items]) => (
          <div key={section}>
            <h4 className="mb-2 text-sm font-semibold">{section}</h4>
            <ul className="space-y-1">{items.map(l => (
              <li key={l.label}><a href={l.url} className="text-sm text-gray-500 hover:text-blue-600">{l.label}</a></li>
            ))}</ul>
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center justify-between text-xs text-gray-400">
        <span>{copyright}</span><span>v{version}</span>
      </div>
    </footer>
  );
}

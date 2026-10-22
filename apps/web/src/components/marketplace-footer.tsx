"use client";

interface Link { label: string; url: string; }
interface MarketplaceFooterProps { sections: Record<string, Link[]>; copyright: string; }

export function MarketplaceFooter({ sections, copyright }: MarketplaceFooterProps) {
  return (
    <footer className="mt-16 border-t border-gray-200 pt-8 dark:border-gray-800">
      <div className="grid grid-cols-2 gap-6 sm:grid-cols-3">
        {Object.entries(sections).map(([title, links]) => (
          <div key={title}>
            <h4 className="mb-2 text-sm font-semibold">{title}</h4>
            <ul className="space-y-1">{links.map(l => (
              <li key={l.label}><a href={l.url} className="text-sm text-gray-500 hover:text-blue-600">{l.label}</a></li>
            ))}</ul>
          </div>
        ))}
      </div>
      <p className="mt-8 text-center text-xs text-gray-400">{copyright}</p>
    </footer>
  );
}

"use client";

interface FooterLink { label: string; href: string; }
interface FooterProps { sections: Record<string, FooterLink[]>; copyright: string; }

export function Footer({ sections, copyright }: FooterProps) {
  return (
    <footer className="border-t py-12 dark:border-gray-800">
      <div className="mx-auto max-w-5xl px-4">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {Object.entries(sections).map(([name, links]) => (
            <div key={name}>
              <h4 className="text-sm font-semibold mb-3">{name}</h4>
              <ul className="space-y-2">
                {links.map(l => (
                  <li key={l.href}>
                    <a href={l.href} className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-white">{l.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-xs text-gray-400">{copyright}</p>
      </div>
    </footer>
  );
}

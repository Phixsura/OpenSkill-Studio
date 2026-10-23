"use client";

interface FooterLink { label: string; url: string; }
interface FooterSection { title: string; links: FooterLink[]; }
interface PlatformFooterProps { sections: FooterSection[]; copyright: string; }

export function PlatformFooter({ sections, copyright }: PlatformFooterProps) {
  return (
    <footer className="border-t dark:border-gray-700 mt-12 pt-8 pb-6">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 mb-8">
        {sections.map(s => (
          <div key={s.title}>
            <h4 className="text-sm font-semibold mb-3">{s.title}</h4>
            <ul className="space-y-1.5">
              {s.links.map(l => (
                <li key={l.label}>
                  <a href={l.url} className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 transition">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center">{copyright}</p>
    </footer>
  );
}

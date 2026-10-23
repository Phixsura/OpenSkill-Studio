"use client";

interface FooterLink { label: string; url: string; }
interface FooterSection { title: string; links: FooterLink[]; }
interface Social { platform: string; url: string; icon: string; }
interface PlatformFooterProps { brand: { name: string; tagline: string };
  sections: FooterSection[]; social: Social[]; copyright: string; }

export function PlatformFooter({ brand, sections, social, copyright }: PlatformFooterProps) {
  return (
    <footer className="border-t pt-10 dark:border-gray-700">
      <div className="grid gap-8 sm:grid-cols-4">
        <div>
          <h2 className="text-lg font-bold">{brand.name}</h2>
          <p className="mt-1 text-sm text-gray-400">{brand.tagline}</p>
          <div className="mt-4 flex gap-3">
            {social.map(s => (
              <a key={s.platform} href={s.url} target="_blank" rel="noopener noreferrer"
                className="flex h-8 w-8 items-center justify-center rounded-full border text-sm dark:border-gray-600">
                {s.icon}
              </a>
            ))}
          </div>
        </div>
        {sections.map(sec => (
          <div key={sec.title}>
            <h3 className="text-sm font-bold">{sec.title}</h3>
            <ul className="mt-3 space-y-2">
              {sec.links.map(link => (
                <li key={link.url}>
                  <a href={link.url} className="text-sm text-gray-400 hover:text-blue-500">{link.label}</a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mt-8 border-t py-4 text-center dark:border-gray-700">
        <p className="text-xs text-gray-400">{copyright}</p>
      </div>
    </footer>
  );
}

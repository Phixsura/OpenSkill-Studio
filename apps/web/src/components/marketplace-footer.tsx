"use client";

interface FooterLink {
  label: string;
  href: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

export function MarketplaceFooter({
  sections,
  version,
  copyright,
}: {
  sections: FooterSection[];
  version: string;
  copyright: string;
}) {
  return (
    <footer className="border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-900 mt-12">
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {sections.map((section) => (
            <div key={section.title}>
              <h3 className="font-semibold text-sm mb-3">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-8 pt-6 border-t dark:border-gray-800 flex flex-col md:flex-row items-center justify-between text-xs text-gray-400">
          <p>{copyright}</p>
          <div className="flex items-center gap-4 mt-2 md:mt-0">
            <span>Platform v{version}</span>
            <span>·</span>
            <a href="/status" className="hover:text-gray-600">Status</a>
            <span>·</span>
            <a href="/privacy" className="hover:text-gray-600">Privacy</a>
            <span>·</span>
            <a href="/terms" className="hover:text-gray-600">Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

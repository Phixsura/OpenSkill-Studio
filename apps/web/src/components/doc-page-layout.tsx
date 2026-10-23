"use client";

interface Heading { level: number; text: string; slug: string; }
interface DocPageLayoutProps { title: string; readTimeDisplay: string;
  headings: Heading[]; hasToc: boolean; children: React.ReactNode; }

export function DocPageLayout({ title, readTimeDisplay, headings, hasToc, children }: DocPageLayoutProps) {
  return (
    <div className="flex gap-8 max-w-5xl mx-auto">
      <article className="flex-1 min-w-0">
        <h1 className="text-2xl font-bold mb-2">{title}</h1>
        <p className="text-xs text-gray-400 mb-6">{readTimeDisplay}</p>
        <div className="prose dark:prose-invert max-w-none">{children}</div>
      </article>
      {hasToc && (
        <nav className="w-56 shrink-0 hidden lg:block">
          <p className="text-xs font-semibold text-gray-400 uppercase mb-2">On this page</p>
          <ul className="space-y-1 text-sm border-l border-gray-200 dark:border-gray-700">
            {headings.map(h => (
              <li key={h.slug} style={{ paddingLeft: `${(h.level - 1) * 12}px` }}>
                <a href={`#${h.slug}`} className="block py-0.5 pl-3 text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 border-l-2 border-transparent hover:border-blue-500 transition">
                  {h.text}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  );
}

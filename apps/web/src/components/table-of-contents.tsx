"use client";

interface TocItem { level: number; text: string; slug: string; }
interface TableOfContentsProps { items: TocItem[]; activeSlug?: string; }

export function TableOfContents({ items, activeSlug }: TableOfContentsProps) {
  return (
    <nav className="space-y-0.5">
      <p className="text-xs font-semibold text-gray-400 uppercase mb-2">On this page</p>
      {items.map((item, i) => (
        <a key={i} href={`#${item.slug}`}
          style={{ paddingLeft: (item.level - 1) * 12 }}
          className={`block rounded px-2 py-1 text-sm transition hover:bg-gray-100 dark:hover:bg-gray-800 ${activeSlug === item.slug ? "text-blue-600 font-medium bg-blue-50 dark:bg-blue-900/10" : "text-gray-600 dark:text-gray-400"}`}>
          {item.text}
        </a>
      ))}
    </nav>
  );
}

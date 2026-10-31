"use client";

interface Heading { level: number; text: string; id: string; }
interface MarkdownContentViewProps { htmlContent: string; headings: Heading[];
  showToc: boolean; }

export function MarkdownContentView({ htmlContent, headings, showToc }: MarkdownContentViewProps) {
  return (
    <div className="flex gap-6">
      {showToc && headings.length > 0 && (
        <nav className="hidden w-48 flex-shrink-0 lg:block">
          <h3 className="text-xs font-semibold uppercase text-gray-400">Contents</h3>
          <ul className="mt-2 space-y-1">
            {headings.map(h => (
              <li key={h.id} style={{ paddingLeft: `${(h.level - 1) * 12}px` }}>
                <a href={`#${h.id}`} className="text-xs text-gray-500 hover:text-blue-500">{h.text}</a>
              </li>
            ))}
          </ul>
        </nav>
      )}
      <div className="prose max-w-none flex-1 dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: htmlContent }} />
    </div>
  );
}

"use client";

interface ContentBlock { type: string; text?: string; level?: number;
  code?: string; language?: string; }
interface MarkdownContentProps { blocks: ContentBlock[]; }

export function MarkdownContent({ blocks }: MarkdownContentProps) {
  return (
    <div className="prose dark:prose-invert max-w-none">
      {blocks.map((b, i) => {
        if (b.type === "heading") {
          const Tag = `h${Math.min(b.level || 1, 6)}` as keyof JSX.IntrinsicElements;
          return <Tag key={i} className="font-bold mt-4 mb-2">{b.text}</Tag>;
        }
        if (b.type === "code") {
          return (
            <div key={i} className="relative">
              {b.language && <span className="absolute top-2 right-2 text-xs text-gray-400">{b.language}</span>}
              <pre className="bg-gray-900 text-gray-300 rounded-lg p-4 text-xs overflow-auto"><code>{b.code}</code></pre>
            </div>
          );
        }
        return <p key={i} className="text-sm leading-relaxed mb-3">{b.text}</p>;
      })}
    </div>
  );
}

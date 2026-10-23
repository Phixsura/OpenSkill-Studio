"use client";

interface Snippet { id: string; title: string; language: string; tags: string[]; preview: string; }
interface CodeSnippetBrowserProps { snippets: Snippet[]; onCopy: (id: string) => void; }

const LANG_COLOR: Record<string, string> = {
  python: "bg-yellow-100 text-yellow-700", typescript: "bg-blue-100 text-blue-700",
  javascript: "bg-yellow-100 text-yellow-700", go: "bg-cyan-100 text-cyan-700",
  rust: "bg-orange-100 text-orange-700",
};

export function CodeSnippetBrowser({ snippets, onCopy }: CodeSnippetBrowserProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📝 Code Snippets</h3>
      <div className="space-y-3">
        {snippets.map(s => (
          <div key={s.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{s.title}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${LANG_COLOR[s.language] || "bg-gray-100"}`}>{s.language}</span>
              </div>
              <button onClick={() => onCopy(s.id)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Copy</button>
            </div>
            <pre className="text-xs font-mono text-gray-500 overflow-hidden">{s.preview}</pre>
            {s.tags.length > 0 && (
              <div className="flex gap-1 mt-2">
                {s.tags.map(t => <span key={t} className="text-xs bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded">{t}</span>)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

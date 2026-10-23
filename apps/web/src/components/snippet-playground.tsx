"use client";

interface SnippetPlaygroundProps { languages: string[]; currentLanguage: string;
  output: string; running: boolean; onRun: (code: string) => void;
  onLanguageChange: (lang: string) => void; }

export function SnippetPlayground({ languages, currentLanguage, output, running, onRun, onLanguageChange }: SnippetPlaygroundProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-3 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">▶️ Playground</h3>
        <div className="flex gap-2">
          <select value={currentLanguage} onChange={e => onLanguageChange(e.target.value)}
            className="text-xs border rounded px-2 py-0.5 dark:bg-gray-800 dark:border-gray-600">
            {languages.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
          <button onClick={() => onRun("")} disabled={running}
            className="px-3 py-0.5 text-xs bg-green-500 text-white rounded disabled:opacity-50">
            {running ? "Running..." : "▶ Run"}
          </button>
        </div>
      </div>
      {output && (
        <div className="bg-gray-900 text-green-400 p-3 font-mono text-xs max-h-32 overflow-y-auto">
          {output}
        </div>
      )}
    </div>
  );
}

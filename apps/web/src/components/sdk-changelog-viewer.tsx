"use client";

interface SdkRelease { version: string; date: string; changes: string[]; breaking: boolean; }
interface SdkChangelogViewerProps { languages: string[]; releases: Record<string, SdkRelease[]>;
  selectedLang: string; onSelectLang: (lang: string) => void; }

const LANG_ICON: Record<string, string> = {
  typescript: "🟦", python: "🐍", go: "🔵", java: "☕", ruby: "💎",
};

export function SdkChangelogViewer({ languages, releases, selectedLang, onSelectLang }: SdkChangelogViewerProps) {
  const langReleases = releases[selectedLang] || [];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-2">📦 SDK Changelog</h3>
        <div className="flex gap-1">
          {languages.map(l => (
            <button key={l} onClick={() => onSelectLang(l)}
              className={`text-xs px-3 py-1 rounded capitalize ${
                l === selectedLang ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"
              }`}>{LANG_ICON[l] || ""} {l}</button>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {langReleases.map(r => (
          <div key={r.version} className="px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold font-mono">v{r.version}</span>
              <span className="text-xs text-gray-400">{r.date}</span>
              {r.breaking && <span className="text-xs px-1.5 py-0.5 rounded bg-red-100 text-red-700">Breaking</span>}
            </div>
            <ul className="text-xs text-gray-500 space-y-0.5">
              {r.changes.map((c, i) => <li key={i}>• {c}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

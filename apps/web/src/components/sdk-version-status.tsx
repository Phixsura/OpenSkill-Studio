"use client";

interface SdkInfo { language: string; pkg: string; latest: string; }
interface SdkVersionStatusProps { sdks: SdkInfo[]; onInstall: (language: string) => void; }

const LANG_ICON: Record<string, string> = {
  typescript: "🟦", python: "🐍", go: "🔵", java: "☕", ruby: "💎",
};

export function SdkVersionStatus({ sdks, onInstall }: SdkVersionStatusProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📦 SDKs</h3>
      <div className="space-y-2">
        {sdks.map(s => (
          <div key={s.language} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{LANG_ICON[s.language] || "📦"}</span>
              <span className="text-sm font-medium capitalize">{s.language}</span>
              <span className="text-xs text-gray-400 font-mono">{s.pkg}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono">v{s.latest}</span>
              <button onClick={() => onInstall(s.language)}
                className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded hover:bg-blue-700">Install</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

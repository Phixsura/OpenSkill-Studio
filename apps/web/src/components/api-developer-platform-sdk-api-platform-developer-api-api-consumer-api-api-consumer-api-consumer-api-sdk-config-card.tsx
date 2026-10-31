"use client";

interface Config { id: string; language: string; baseUrl: string; version: string; timeoutMs: number; retries: number; }
interface Props { configs: Config[]; consumerId: string; appName: string; }

const langIcons: Record<string, string> = { typescript: "TS", python: "PY", go: "GO", java: "JV", ruby: "RB", csharp: "C#", php: "PHP" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfigCard({ configs, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ SDK Configs</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{langIcons[c.language] ?? c.language}</span>
                  <code className="text-gray-600 dark:text-gray-400">{c.baseUrl || "—"}</code>
                </div>
                <span className="text-gray-400">{c.version}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">Timeout: {c.timeoutMs}ms · {c.retries} retries</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

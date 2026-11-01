"use client";

interface ConfigInfo { destination: string; headers: Record<string, string>; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiWebhookHeaderManagerCard({ configs, appName }: Props) {
  const totalHeaders = configs.reduce((s, c) => s + Object.keys(c.headers).length, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📨 Custom Headers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalHeaders} headers across {configs.length} destinations</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom headers</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.destination} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <p className="text-[11px] font-medium text-gray-700 dark:text-gray-300 mb-1">{new URL(c.destination).hostname}</p>
              <div className="flex flex-wrap gap-1">
                {Object.entries(c.headers).map(([k, v]) => (
                  <span key={k} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] font-mono text-blue-700 dark:bg-blue-900 dark:text-blue-200">{k}: {v}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

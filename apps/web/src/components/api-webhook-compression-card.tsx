"use client";
interface CompInfo { destination: string; algorithm: string; bytes_saved: number; }
interface APIWebhookCompressionCardProps { configs: CompInfo[]; appName: string; }

function formatBytes(b: number): string {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export default function APIWebhookCompressionCard({ configs, appName }: APIWebhookCompressionCardProps) {
  const totalSaved = configs.reduce((s, c) => s + c.bytes_saved, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Compression</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{formatBytes(totalSaved)} saved</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compression configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="truncate max-w-[160px] text-gray-700 dark:text-gray-300">{c.destination}</span>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{c.algorithm}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

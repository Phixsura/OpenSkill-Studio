"use client";

interface ConfigInfo { destination: string; algorithm: string; key_fingerprint: string; enabled: boolean; payloads_encrypted: number; }
interface Props { configs: ConfigInfo[]; stats: { destinations: number; payloads_encrypted: number; bytes_encrypted: number }; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperAPIApiWebhookPayloadEncryptionCard({ configs, stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Payload Encryption</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{fmtSize(stats.bytes_encrypted)} encrypted</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No encryption configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${c.enabled ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-gray-700 dark:text-gray-300">{new URL(c.destination).hostname}</span>
              </div>
              <span className="font-mono text-[10px] text-gray-400">{c.algorithm} · {c.payloads_encrypted} enc</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

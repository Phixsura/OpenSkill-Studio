"use client";

interface EntryInfo { entry_id: string; credential_type: string; name: string; fingerprint: string; access_count: number; rotated: boolean; }
interface Props { entries: EntryInfo[]; appName: string; }

const tIcon: Record<string, string> = { api_key: "🔑", oauth_token: "🎫", jwt_secret: "📜", webhook_secret: "🔐" };

export default function APIDeveloperAPIApiDeveloperCredentialVaultCard({ entries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Credential Vault</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {entries.length} credentials</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No credentials stored</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center gap-1.5">
                <span>{tIcon[e.credential_type] ?? "•"}</span>
                <div>
                  <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{e.name}</span>
                  <p className="font-mono text-[9px] text-gray-400">{e.fingerprint}...</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-gray-400">{e.access_count} uses</span>
                {e.rotated && <p className="text-[9px] text-blue-500">rotated</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

interface CredentialInfo {
  credential_id: string;
  name: string;
  prefix: string;
  version: number;
  rotated_at: string | null;
}

interface CredentialVaultCardProps {
  credentials: CredentialInfo[];
  appName: string;
}

function timeAgo(iso: string | null): string {
  if (!iso) return "never";
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function CredentialVaultCard({ credentials, appName }: CredentialVaultCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Credential Vault
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">🔒 {credentials.length} stored</span>
      </div>

      {credentials.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No credentials stored</p>
      ) : (
        <div className="space-y-1.5">
          {credentials.map((c) => (
            <div
              key={c.credential_id}
              className="flex items-center justify-between rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm">🔑</span>
                <div>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{c.name}</span>
                  <p className="font-mono text-[10px] text-gray-400">{c.prefix}••••••••</p>
                </div>
              </div>
              <div className="text-right text-[11px] text-gray-400">
                <p>v{c.version}</p>
                <p>rotated {timeAgo(c.rotated_at)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

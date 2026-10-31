"use client";

interface SecretEntry { key: string; fingerprint: string; version: number; owner: string; }
interface SecretsVaultPanelProps { secrets: SecretEntry[]; totalAccesses: number; }

export function SecretsVaultPanel({ secrets, totalAccesses }: SecretsVaultPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Secrets Vault</h3>
        <span className="text-xs text-gray-400">{secrets.length} secrets · {totalAccesses} accesses</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {secrets.map(s => (
          <div key={s.key} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{s.key}</span>
              <span className="text-gray-400 ml-2">v{s.version} · {s.owner}</span>
            </div>
            <span className="font-mono text-gray-400">{s.fingerprint}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

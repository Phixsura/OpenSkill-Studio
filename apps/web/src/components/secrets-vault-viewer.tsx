"use client";

interface SecretEntry { name: string; version: number; accessCount: number; owner: string; }
interface SecretsVaultViewerProps { secrets: SecretEntry[]; totalSecrets: number;
  totalAccesses: number; onRotate: (name: string) => void; }

export function SecretsVaultViewer({ secrets, totalSecrets, totalAccesses, onRotate }: SecretsVaultViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Secrets Vault</h3>
        <span className="text-xs text-gray-400">{totalSecrets} secrets · {totalAccesses} accesses</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {secrets.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-mono">{s.name}</div>
              <div className="text-[10px] text-gray-400">v{s.version} · {s.accessCount} accesses · {s.owner}</div>
            </div>
            <button onClick={() => onRotate(s.name)} className="px-2 py-1 text-xs text-blue-500 hover:underline">🔄 Rotate</button>
          </div>
        ))}
      </div>
    </div>
  );
}

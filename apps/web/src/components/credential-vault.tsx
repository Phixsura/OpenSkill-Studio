"use client";

interface Credential { id: string; name: string; preview: string; status: string; expiresAt: string; }
interface CredentialVaultProps { credentials: Credential[]; expired: string[]; expiringSoon: string[];
  onRotate: (id: string) => void; }

export function CredentialVault({ credentials, expired, expiringSoon, onRotate }: CredentialVaultProps) {
  const expSet = new Set([...expired, ...expiringSoon]);
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">🔐 Credential Vault</h3>
        {expSet.size > 0 && <span className="text-xs text-red-600">{expSet.size} need attention</span>}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {credentials.map(c => (
          <div key={c.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <code className="text-sm font-mono font-medium">{c.name}</code>
              <p className="text-xs text-gray-400 mt-0.5">{c.preview}</p>
            </div>
            <div className="flex items-center gap-2">
              {expired.includes(c.name) && <span className="text-xs text-red-500">Expired</span>}
              {expiringSoon.includes(c.name) && <span className="text-xs text-yellow-600">Expiring</span>}
              <button onClick={() => onRotate(c.id)} className="text-xs text-blue-600 hover:underline">Rotate</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

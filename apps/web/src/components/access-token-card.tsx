"use client";

interface AccessTokenCardProps { prefix: string; scopes: string[]; issuedAt: string;
  expiresAt: string; onRevoke: () => void; }

export function AccessTokenCard({ prefix, scopes, issuedAt, expiresAt, onRevoke }: AccessTokenCardProps) {
  const expired = new Date(expiresAt) < new Date();
  return (
    <div className={`rounded-lg border p-4 dark:border-gray-700 ${expired ? "opacity-50" : ""}`}>
      <div className="flex items-center justify-between">
        <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{prefix}••••••••</code>
        {expired ? (
          <span className="text-xs text-red-500">Expired</span>
        ) : (
          <button onClick={onRevoke} className="text-xs text-red-600 hover:underline">Revoke</button>
        )}
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {scopes.map(s => (
          <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{s}</span>
        ))}
      </div>
      <div className="mt-2 text-xs text-gray-400">
        <span>Issued: {new Date(issuedAt).toLocaleDateString()}</span>
        <span className="mx-2">·</span>
        <span>Expires: {new Date(expiresAt).toLocaleDateString()}</span>
      </div>
    </div>
  );
}

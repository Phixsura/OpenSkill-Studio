"use client";

interface TokenIntrospectionCardProps {
  active: boolean; appId: string; scopes: string[];
  issuedAt: string; expiresAt: string | null; expired: boolean; revoked: boolean;
}

export function TokenIntrospectionCard({ active, appId, scopes, issuedAt, expiresAt, expired, revoked }: TokenIntrospectionCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${active ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Token Details</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {active ? "Active" : expired ? "Expired" : revoked ? "Revoked" : "Inactive"}
        </span>
      </div>
      <div className="mt-3 space-y-1 text-sm">
        <p><span className="text-gray-400">App:</span> <code className="text-xs">{appId}</code></p>
        <p><span className="text-gray-400">Issued:</span> {issuedAt}</p>
        {expiresAt && <p><span className="text-gray-400">Expires:</span> {expiresAt}</p>}
        <div>
          <span className="text-gray-400">Scopes:</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {scopes.map(s => <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">{s}</span>)}
          </div>
        </div>
      </div>
    </div>
  );
}

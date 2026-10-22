"use client";

interface TokenInfoCardProps {
  active: boolean;
  scope?: string;
  clientId?: string;
  expiresAt?: string;
}

export function TokenInfoCard({ active, scope, clientId, expiresAt }: TokenInfoCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${active ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xl">{active ? "🟢" : "🔴"}</span>
        <span className="font-semibold">{active ? "Active Token" : "Inactive Token"}</span>
      </div>
      {clientId && <p className="text-sm"><span className="text-gray-500">Client:</span> <code className="text-xs">{clientId}</code></p>}
      {scope && <p className="text-sm"><span className="text-gray-500">Scope:</span> {scope}</p>}
      {expiresAt && <p className="text-sm"><span className="text-gray-500">Expires:</span> {expiresAt}</p>}
    </div>
  );
}

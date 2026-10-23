"use client";

interface TokenRefreshStatusProps { accessExpiresAt: string; refreshExpiresAt: string;
  tokenType: string; onRefresh: () => void; }

export function TokenRefreshStatus({ accessExpiresAt, refreshExpiresAt, tokenType, onRefresh }: TokenRefreshStatusProps) {
  const now = new Date();
  const accessExpired = new Date(accessExpiresAt) < now;
  const refreshExpired = new Date(refreshExpiresAt) < now;
  const accessMinLeft = Math.max(0, Math.round((new Date(accessExpiresAt).getTime() - now.getTime()) / 60000));

  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Token Status</h3>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{tokenType}</span>
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span>Access Token</span>
          <span className={accessExpired ? "text-red-600" : "text-green-600"}>
            {accessExpired ? "Expired" : `${accessMinLeft}m remaining`}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span>Refresh Token</span>
          <span className={refreshExpired ? "text-red-600" : "text-green-600"}>
            {refreshExpired ? "Expired" : "Active"}
          </span>
        </div>
      </div>
      {accessExpired && !refreshExpired && (
        <button onClick={onRefresh} className="mt-3 w-full rounded bg-blue-600 py-2 text-sm text-white">Refresh Token</button>
      )}
    </div>
  );
}

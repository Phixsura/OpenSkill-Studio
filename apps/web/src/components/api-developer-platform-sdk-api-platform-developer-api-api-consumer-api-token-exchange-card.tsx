"use client";

interface Props { pendingCodes: number; totalExchanges: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchangeCard({ pendingCodes, totalExchanges, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Token Exchange</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — OAuth2 Authorization Code Flow</p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-yellow-600 dark:text-yellow-400">{pendingCodes}</div><div className="text-gray-400">Pending Codes</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{totalExchanges}</div><div className="text-gray-400">Exchanges</div></div>
      </div>
    </div>
  );
}

"use client";
export function FleetApiKeyRotationV9Panel({ keys, expired }: { keys: number; expired: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 API Key Rotation v9</h3>
    <div className="text-sm">{keys} keys · {expired} expired</div>
  </div>);
}

"use client";
export function FleetIamPanel({ total, withMfa, unusedKeys, admins, secure }: { total: number; withMfa: number; unusedKeys: number; admins: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 IAM</h3>
    <div className="text-sm">{withMfa}/{total} MFA · {admins} admins</div>
    {!secure && <span className="text-xs text-red-500">⚠️ {unusedKeys} unused keys</span>}
  </div>);
}

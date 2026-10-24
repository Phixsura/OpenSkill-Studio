"use client";
export function FleetSigstorePanel({ total, signed, verified, unsigned, secure }: { total: number; signed: number; verified: number; unsigned: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✍️ Sigstore</h3>
    <div className="text-sm">{signed}/{total} signed · {verified} verified</div>
    {!secure && <span className="text-xs text-yellow-600">⚠️ {unsigned} unsigned</span>}
  </div>);
}

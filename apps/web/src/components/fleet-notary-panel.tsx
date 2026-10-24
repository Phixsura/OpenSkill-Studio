"use client";
export function FleetNotaryPanel({ total, signed, trusted, unsigned }: { total: number; signed: number; trusted: number; unsigned: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✍️ Notary</h3>
    <div className="text-sm">{signed}/{total} signed · {trusted} trusted</div>
    {unsigned > 0 && <span className="text-xs text-yellow-600">⚠️ {unsigned} unsigned</span>}
  </div>);
}

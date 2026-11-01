"use client";
export function FleetEnvVariableV9Panel({ total, encrypted }: { total: number; encrypted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Env Variables v9</h3>
    <div className="text-sm">{total} vars · {encrypted} encrypted</div>
  </div>);
}

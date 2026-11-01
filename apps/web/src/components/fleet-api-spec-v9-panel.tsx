"use client";
export function FleetApiSpecV9Panel({ specs, valid }: { specs: number; valid: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 API Spec v9</h3>
    <div className="text-sm">{specs} specs · {valid} valid</div>
  </div>);
}

"use client";
export function FleetConfigValidationV9Panel({ configs, invalid }: { configs: number; invalid: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Config Validation v9</h3>
    <div className="text-sm">{configs} configs · {invalid} invalid</div>
  </div>);
}

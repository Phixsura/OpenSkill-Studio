"use client";
export function FleetApiDataValidationV9Panel({ validators, anomalies }: { validators: number; anomalies: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Data Validation v9</h3>
    <div className="text-sm">{validators} validators · {anomalies} anomalies</div>
  </div>);
}

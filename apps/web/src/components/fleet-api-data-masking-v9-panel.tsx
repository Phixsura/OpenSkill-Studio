"use client";
export function FleetApiDataMaskingV9Panel({ endpoints, piiFields }: { endpoints: number; piiFields: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Data Masking v9</h3>
    <div className="text-sm">{endpoints} endpoints · {piiFields} PII fields masked</div>
  </div>);
}

"use client";
export function FleetApiOutputEncodingV9Panel({ endpoints, encoded }: { endpoints: number; encoded: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Output Encoding v9</h3>
    <div className="text-sm">{endpoints} endpoints · {encoded} encoded</div>
  </div>);
}

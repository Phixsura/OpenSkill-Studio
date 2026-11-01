"use client";
export function FleetApiContentNegotiationV9Panel({ endpoints, json }: { endpoints: number; json: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 Content Negotiation v9</h3>
    <div className="text-sm">{endpoints} endpoints · {json} JSON</div>
  </div>);
}

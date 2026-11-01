"use client";
export function FleetSolrPanel({ collections, active, documents, qps }: { collections: number; active: number; documents: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Solr</h3>
    <div className="text-sm">{active}/{collections} active · {documents.toLocaleString()} docs · {qps.toLocaleString()} qps</div>
  </div>);
}

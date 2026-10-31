"use client";
export function FleetAiDocLoaderPanel({ loaders, active, formats, docs, sizeGb }: { loaders: number; active: number; formats: number; docs: number; sizeGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 AI Document Loader</h3>
    <div className="text-sm">{active}/{loaders} active · {formats} formats · {docs.toLocaleString()} docs · {sizeGb}GB</div>
  </div>);
}

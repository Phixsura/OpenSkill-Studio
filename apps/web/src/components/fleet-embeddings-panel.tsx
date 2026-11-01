"use client";
export function FleetEmbeddingsPanel({ services, active, embeddings, maxDimensions }: { services: number; active: number; embeddings: number; maxDimensions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 Embeddings</h3>
    <div className="text-sm">{active}/{services} active · {embeddings.toLocaleString()} embeds · {maxDimensions}d</div>
  </div>);
}

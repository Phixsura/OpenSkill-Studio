"use client";
export function FleetAiEmbeddingsPanel({ pipelines, active, vectors, dims }: { pipelines: number; active: number; vectors: number; dims: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧬 AI Embeddings</h3>
    <div className="text-sm">{active}/{pipelines} active · {vectors.toLocaleString()} vectors · {dims}d</div>
  </div>);
}

"use client";
export function FleetChromaPanel({ collections, documents, embeddings, synced }: { collections: number; documents: number; embeddings: number; synced: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎨 Chroma</h3>
    <div className="text-sm">{collections} collections · {documents.toLocaleString()} docs · {embeddings.toLocaleString()} embeddings</div>
    {!synced && <span className="text-xs text-yellow-600">⚠️ Out of sync</span>}
  </div>);
}

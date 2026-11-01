"use client";
export function FleetAiChunkerPanel({ chunkers, active, docs, chunks, avgTokens }: { chunkers: number; active: number; docs: number; chunks: number; avgTokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✂️ AI Chunker</h3>
    <div className="text-sm">{active}/{chunkers} active · {docs.toLocaleString()} docs · {chunks.toLocaleString()} chunks · {avgTokens} avg tokens</div>
  </div>);
}

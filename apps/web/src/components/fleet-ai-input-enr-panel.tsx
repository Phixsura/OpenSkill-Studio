"use client";
export function FleetAiInputEnrPanel({ enrichers, active, enriched, sources, addedTokens }: { enrichers: number; active: number; enriched: number; sources: number; addedTokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✨ AI Input Enricher</h3>
    <div className="text-sm">{active}/{enrichers} active · {enriched.toLocaleString()} enriched · {sources} sources · +{addedTokens} tokens</div>
  </div>);
}

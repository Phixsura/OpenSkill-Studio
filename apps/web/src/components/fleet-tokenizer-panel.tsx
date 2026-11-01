"use client";
export function FleetTokenizerPanel({ services, active, tokens, vocabularies }: { services: number; active: number; tokens: number; vocabularies: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔤 Tokenizer</h3>
    <div className="text-sm">{active}/{services} active · {tokens.toLocaleString()} tokens · {vocabularies} vocabs</div>
  </div>);
}

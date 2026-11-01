"use client";
export function FleetAiTextExtPanel({ extractors, active, extracted, types, accuracy }: { extractors: number; active: number; extracted: number; types: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 AI Text Extractor</h3>
    <div className="text-sm">{active}/{extractors} active · {extracted.toLocaleString()} extracted · {types} types · {accuracy}% acc</div>
  </div>);
}

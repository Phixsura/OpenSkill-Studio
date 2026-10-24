"use client";
export function FleetAiApiDocsPanel({ generators, active, endpoints, examples, views }: { generators: number; active: number; endpoints: number; examples: number; views: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 AI API Docs</h3>
    <div className="text-sm">{active}/{generators} active · {endpoints} endpoints · {examples} examples · {views.toLocaleString()} views</div>
  </div>);
}

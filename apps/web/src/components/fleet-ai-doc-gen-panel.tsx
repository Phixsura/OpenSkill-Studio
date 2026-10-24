"use client";
export function FleetAiDocGenPanel({ generators, active, pages, repos, freshness }: { generators: number; active: number; pages: number; repos: number; freshness: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 AI Doc Generation</h3>
    <div className="text-sm">{active}/{generators} active · {pages.toLocaleString()} pages · {repos} repos · {freshness}% fresh</div>
  </div>);
}

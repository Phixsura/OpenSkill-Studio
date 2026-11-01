"use client";
export function FleetAiDocsV7Panel({ systems, active, pages, examples, satisfaction, coverage }: { systems: number; active: number; pages: number; examples: number; satisfaction: number; coverage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 AI Docs v7</h3>
    <div className="text-sm">{active}/{systems} active · {pages.toLocaleString()} pages · {examples.toLocaleString()} examples · {satisfaction}% sat · {coverage}% coverage</div>
  </div>);
}

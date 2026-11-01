"use client";
export function FleetAiInnovationV7Panel({ trackers, active, experiments, breakthroughs, patents, papers }: { trackers: number; active: number; experiments: number; breakthroughs: number; patents: number; papers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 AI Innovation v7</h3>
    <div className="text-sm">{active}/{trackers} active · {experiments} experiments · {breakthroughs} breakthroughs · {patents} patents · {papers} papers</div>
  </div>);
}

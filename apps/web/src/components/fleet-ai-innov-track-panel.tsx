"use client";
export function FleetAiInnovTrackPanel({ trackers, active, experiments, breakthroughs, papers }: { trackers: number; active: number; experiments: number; breakthroughs: number; papers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 AI Innovation Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {experiments} experiments · {breakthroughs} breakthroughs · {papers} papers</div>
  </div>);
}

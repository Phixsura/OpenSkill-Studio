"use client";
export function FleetAiConstTrainPanel({ trainers, active, principles, revisions, alignment }: { trainers: number; active: number; principles: number; revisions: number; alignment: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Constitutional Training</h3>
    <div className="text-sm">{active}/{trainers} active · {principles} principles · {revisions.toLocaleString()} revisions · {alignment}% aligned</div>
  </div>);
}

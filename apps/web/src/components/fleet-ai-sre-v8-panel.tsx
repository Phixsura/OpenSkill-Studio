"use client";
export function FleetAiSreV8Panel({ teams, active, toil, budget, slos }: { teams: number; active: number; toil: number; budget: number; slos: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI SRE v8</h3>
    <div className="text-sm">{active}/{teams} active · {toil}% toil · {budget}% budget · {slos} SLOs</div>
  </div>);
}

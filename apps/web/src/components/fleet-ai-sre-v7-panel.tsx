"use client";
export function FleetAiSreV7Panel({ teams, active, toil, budget, slos, mttr }: { teams: number; active: number; toil: number; budget: number; slos: number; mttr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI SRE v7</h3>
    <div className="text-sm">{active}/{teams} active · {toil}% toil · {budget}% budget · {slos} SLOs · MTTR {mttr}m</div>
  </div>);
}

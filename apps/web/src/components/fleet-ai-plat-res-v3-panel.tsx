"use client";
export function FleetAiPlatResV3Panel({ systems, active, blastRadius, recovery, chaosScore }: { systems: number; active: number; blastRadius: number; recovery: number; chaosScore: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Resilience v3</h3>
    <div className="text-sm">{active}/{systems} active · {blastRadius}% blast radius · {recovery}s recovery · chaos {chaosScore}</div>
  </div>);
}

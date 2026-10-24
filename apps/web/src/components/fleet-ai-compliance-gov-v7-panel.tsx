"use client";
export function FleetAiComplianceGovV7Panel({ frameworks, active, regulations, controls, passed, score }: { frameworks: number; active: number; regulations: number; controls: number; passed: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Compliance Gov v7</h3>
    <div className="text-sm">{active}/{frameworks} active · {regulations} regs · {controls} controls · {passed} passed · score {score}</div>
  </div>);
}

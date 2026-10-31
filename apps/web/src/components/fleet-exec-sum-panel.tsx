"use client";
const GC: Record<string, string> = { Elite: "text-green-600", High: "text-blue-500", Medium: "text-yellow-600" };
export function FleetExecSumPanel({ uptimePct, deployFreq, mttrMin, cfrPct, doraGrade }: { uptimePct: number; deployFreq: number; mttrMin: number; cfrPct: number; doraGrade: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">📊 Executive Summary</h3>
    <div className={`text-2xl font-black ${GC[doraGrade] ?? ""}`}>DORA: {doraGrade}</div>
    <div className="grid grid-cols-2 gap-2 mt-2 text-xs text-gray-400">
      <span>{uptimePct}% uptime</span><span>{deployFreq}/day deploys</span>
      <span>{mttrMin}min MTTR</span><span>{cfrPct}% CFR</span>
    </div>
  </div>);
}

"use client";
export function FleetAiExpLogPanel({ loggers, active, experiments, runs, artifacts }: { loggers: number; active: number; experiments: number; runs: number; artifacts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Experiment Log</h3>
    <div className="text-sm">{active}/{loggers} active · {experiments.toLocaleString()} experiments · {runs.toLocaleString()} runs · {artifacts.toLocaleString()} artifacts</div>
  </div>);
}

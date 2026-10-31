"use client";
export function FleetAiDiffusionPanel({ models, active, generations, steps, fid }: { models: number; active: number; generations: number; steps: number; fid: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌀 AI Diffusion Model</h3>
    <div className="text-sm">{active}/{models} active · {generations.toLocaleString()} gens · {steps} steps · FID {fid}</div>
  </div>);
}

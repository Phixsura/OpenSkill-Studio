"use client";
export function FleetAiInfProfPanel({ profilers, active, profiles, tokenizeMs, inferenceMs }: { profilers: number; active: number; profiles: number; tokenizeMs: number; inferenceMs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Inference Profiler</h3>
    <div className="text-sm">{active}/{profilers} active · {profiles.toLocaleString()} profiles · tok {tokenizeMs}ms · inf {inferenceMs}ms</div>
  </div>);
}

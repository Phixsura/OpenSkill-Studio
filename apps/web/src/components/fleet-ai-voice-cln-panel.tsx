"use client";
export function FleetAiVoiceClnPanel({ systems, active, voices, generations, mos }: { systems: number; active: number; voices: number; generations: number; mos: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎤 AI Voice Clone</h3>
    <div className="text-sm">{active}/{systems} active · {voices.toLocaleString()} voices · {generations.toLocaleString()} gens · MOS {mos}</div>
  </div>);
}

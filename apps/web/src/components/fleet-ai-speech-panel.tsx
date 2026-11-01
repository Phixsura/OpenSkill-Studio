"use client";
export function FleetAiSpeechPanel({ services, active, hours, languages, wer }: { services: number; active: number; hours: number; languages: number; wer: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗣️ AI Speech</h3>
    <div className="text-sm">{active}/{services} active · {hours.toLocaleString()}h processed · {languages} langs · WER {wer}%</div>
  </div>);
}

"use client";
export function FleetAiSpeechPanel({ services, active, sttHours, ttsChars }: { services: number; active: number; sttHours: number; ttsChars: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔊 AI Speech</h3>
    <div className="text-sm">{active}/{services} active · {sttHours.toLocaleString()}h STT · {ttsChars.toLocaleString()} TTS chars</div>
  </div>);
}

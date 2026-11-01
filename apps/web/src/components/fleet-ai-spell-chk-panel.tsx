"use client";
export function FleetAiSpellChkPanel({ checkers, active, checked, corrections, accuracy }: { checkers: number; active: number; checked: number; corrections: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Spell Check</h3>
    <div className="text-sm">{active}/{checkers} active · {checked.toLocaleString()} checked · {corrections.toLocaleString()} corrections · {accuracy}% acc</div>
  </div>);
}

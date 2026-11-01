"use client";
export function FleetAiModelDbgV2Panel({ debuggers, active, sessions, breakpoints, resolved }: { debuggers: number; active: number; sessions: number; breakpoints: number; resolved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 AI Model Debugger v2</h3>
    <div className="text-sm">{active}/{debuggers} active · {sessions.toLocaleString()} sessions · {breakpoints} breakpoints · {resolved} resolved</div>
  </div>);
}

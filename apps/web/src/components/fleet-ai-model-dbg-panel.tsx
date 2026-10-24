"use client";
export function FleetAiModelDbgPanel({ debuggers, active, sessions, issues, fixed }: { debuggers: number; active: number; sessions: number; issues: number; fixed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 AI Model Debugger</h3>
    <div className="text-sm">{active}/{debuggers} active · {sessions.toLocaleString()} sessions · {issues} issues · {fixed} fixed</div>
  </div>);
}

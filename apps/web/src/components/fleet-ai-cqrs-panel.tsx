"use client";
export function FleetAiCqrsPanel({ handlers, active, commands, queries, cmdMs }: { handlers: number; active: number; commands: number; queries: number; cmdMs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI CQRS</h3>
    <div className="text-sm">{active}/{handlers} active · {commands.toLocaleString()} cmds · {queries.toLocaleString()} queries · {cmdMs}ms cmd</div>
  </div>);
}

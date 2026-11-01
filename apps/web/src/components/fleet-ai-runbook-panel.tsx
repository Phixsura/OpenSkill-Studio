"use client";
export function FleetAiRunbookPanel({ runbooks, active, executions, autoResolved, duration }: { runbooks: number; active: number; executions: number; autoResolved: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Runbook</h3>
    <div className="text-sm">{active}/{runbooks} active · {executions} exec · {autoResolved} auto-resolved · {duration}s avg</div>
  </div>);
}

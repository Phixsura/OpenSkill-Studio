"use client";

import { useState } from "react";

interface Breakpoint {
  id: string;
  file: string;
  line: number;
  type: string;
  enabled: boolean;
  hitCount: number;
  condition?: string;
}

interface StackFrame {
  functionName: string;
  file: string;
  line: number;
  locals: Record<string, unknown>;
}

interface DebugSession {
  state: "running" | "paused" | "stepping" | "stopped";
  breakpoints: Breakpoint[];
  callStack: StackFrame[];
  watchExpressions: Record<string, string>;
}

const stateConfig: Record<string, { color: string; label: string }> = {
  running: { color: "bg-green-500", label: "Running" },
  paused: { color: "bg-yellow-500", label: "Paused" },
  stepping: { color: "bg-blue-500", label: "Stepping" },
  stopped: { color: "bg-gray-500", label: "Stopped" },
};

export function DebuggerPanel({
  session,
  onResume,
  onStep,
  onToggleBp,
  onEval,
}: {
  session: DebugSession;
  onResume?: () => void;
  onStep?: (action: string) => void;
  onToggleBp?: (id: string) => void;
  onEval?: (expr: string) => void;
}) {
  const [tab, setTab] = useState<"stack" | "breakpoints" | "watch">("stack");
  const [evalInput, setEvalInput] = useState("");
  const cfg = stateConfig[session.state];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🐛 Debugger</h2>
          <span className={`w-2.5 h-2.5 rounded-full ${cfg.color} animate-pulse`} />
          <span className="text-xs text-gray-500">{cfg.label}</span>
        </div>
        <div className="flex gap-1">
          {session.state === "paused" && (
            <>
              <button onClick={onResume} className="text-xs bg-green-600 text-white px-2 py-1 rounded">▶ Resume</button>
              <button onClick={() => onStep?.("over")} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">⤵ Step</button>
            </>
          )}
        </div>
      </div>

      <div className="flex gap-1">
        {(["stack", "breakpoints", "watch"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "stack" ? "Call Stack" : t === "breakpoints" ? `Breakpoints (${session.breakpoints.length})` : "Watch"}
          </button>
        ))}
      </div>

      {tab === "stack" && (
        <div className="space-y-1 font-mono text-xs">
          {session.callStack.map((frame, i) => (
            <div key={i} className={`rounded-lg border dark:border-gray-700 p-2 ${i === 0 ? "bg-yellow-50 dark:bg-yellow-900/10 border-yellow-400" : ""}`}>
              <div className="font-bold">{frame.functionName}</div>
              <div className="text-gray-500">{frame.file}:{frame.line}</div>
              {Object.keys(frame.locals).length > 0 && (
                <div className="mt-1 text-gray-400">
                  {Object.entries(frame.locals).map(([k, v]) => (
                    <span key={k} className="mr-2">{k}={JSON.stringify(v)}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {session.callStack.length === 0 && <span className="text-gray-500">No active stack</span>}
        </div>
      )}

      {tab === "breakpoints" && (
        <div className="space-y-1">
          {session.breakpoints.map((bp) => (
            <div key={bp.id} className={`rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between ${!bp.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2 text-xs">
                <span className={`w-3 h-3 rounded-full ${bp.enabled ? "bg-red-500" : "bg-gray-400"}`} />
                <code>{bp.file}:{bp.line}</code>
                {bp.condition && <span className="text-purple-500">if {bp.condition}</span>}
                <span className="text-gray-400">×{bp.hitCount}</span>
              </div>
              <button onClick={() => onToggleBp?.(bp.id)}
                className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                {bp.enabled ? "Disable" : "Enable"}
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === "watch" && (
        <div className="space-y-2">
          {Object.entries(session.watchExpressions).map(([name, expr]) => (
            <div key={name} className="text-xs">
              <span className="text-blue-600">{name}</span>: <code className="text-gray-500">{expr}</code>
            </div>
          ))}
          <div className="flex gap-1">
            <input type="text" value={evalInput} onChange={(e) => setEvalInput(e.target.value)}
              placeholder="Evaluate expression..."
              className="flex-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-xs font-mono" />
            <button onClick={() => { onEval?.(evalInput); setEvalInput(""); }}
              className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Eval</button>
          </div>
        </div>
      )}
    </div>
  );
}

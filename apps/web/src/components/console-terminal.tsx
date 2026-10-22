"use client";

import { useState } from "react";

interface HistoryEntry { input: string; output: string; error?: string | null; }
interface ConsoleTerminalProps { history: HistoryEntry[]; onExecute: (code: string) => void; language: string; }

export function ConsoleTerminal({ history, onExecute, language }: ConsoleTerminalProps) {
  const [input, setInput] = useState("");

  const handleSubmit = () => { if (input.trim()) { onExecute(input); setInput(""); } };

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 text-sm">
      <div className="flex items-center gap-2 border-b border-gray-700 px-3 py-2">
        <span className="h-3 w-3 rounded-full bg-red-500" /><span className="h-3 w-3 rounded-full bg-yellow-500" /><span className="h-3 w-3 rounded-full bg-green-500" />
        <span className="ml-2 text-xs text-gray-400">Sandbox Console — {language}</span>
      </div>
      <div className="max-h-64 overflow-y-auto p-3 font-mono text-xs">
        {history.map((h, i) => (
          <div key={i} className="mb-1">
            <div className="text-green-400">{'>'} {h.input}</div>
            {h.error ? <div className="text-red-400">{h.error}</div> : <div className="text-gray-300">{h.output}</div>}
          </div>
        ))}
      </div>
      <div className="flex border-t border-gray-700">
        <span className="px-2 py-2 text-green-400 font-mono text-xs">{'>'}</span>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && handleSubmit()}
          placeholder="Type code..." className="flex-1 bg-transparent py-2 text-xs text-white outline-none font-mono" />
      </div>
    </div>
  );
}

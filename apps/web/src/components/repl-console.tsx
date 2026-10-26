"use client";

import { useState, useRef, useEffect } from "react";

interface ReplResult {
  inputCode: string;
  output: string;
  error: string;
  executionTimeMs: number;
}

export function ReplConsole({
  history,
  runtime,
  onExecute,
  onClear,
}: {
  history: ReplResult[];
  runtime: string;
  onExecute?: (code: string) => void;
  onClear?: () => void;
}) {
  const [input, setInput] = useState("");
  const [historyIdx, setHistoryIdx] = useState(-1);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (endRef.current && endRef.current.scrollIntoView) {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [history.length]);

  const handleSubmit = () => {
    if (input.trim()) {
      onExecute?.(input);
      setInput("");
      setHistoryIdx(-1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === "ArrowUp") {
      const inputs = history.map((h) => h.inputCode);
      if (inputs.length > 0) {
        const newIdx = historyIdx < inputs.length - 1 ? historyIdx + 1 : historyIdx;
        setHistoryIdx(newIdx);
        setInput(inputs[inputs.length - 1 - newIdx]);
      }
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">💻 REPL</h2>
          <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded font-mono">{runtime}</span>
        </div>
        <button onClick={onClear} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Clear</button>
      </div>

      <div className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 max-h-80 overflow-y-auto font-mono text-xs">
        {history.map((entry, i) => (
          <div key={i} className="mb-2">
            <div className="text-blue-400">{'>'} {entry.inputCode}</div>
            {entry.output && <div className="text-green-400 ml-2">{entry.output}</div>}
            {entry.error && <div className="text-red-400 ml-2">Error: {entry.error}</div>}
            <div className="text-gray-600 ml-2 text-[10px]">{entry.executionTimeMs}ms</div>
          </div>
        ))}
        {history.length === 0 && (
          <div className="text-gray-600">Ready. Type an expression and press Enter.</div>
        )}
        <div ref={endRef} />
      </div>

      <div className="flex gap-2">
        <div className="flex-1 relative">
          <span className="absolute left-3 top-2 text-blue-400 font-mono text-sm">{'>'}</span>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter expression..."
            className="w-full rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black pl-7 pr-3 py-2 text-sm font-mono text-green-400" />
        </div>
        <button onClick={handleSubmit}
          className="text-sm bg-blue-600 text-white px-4 rounded-lg">Run</button>
      </div>
    </div>
  );
}

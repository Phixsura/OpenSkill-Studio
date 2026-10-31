"use client";

import { useState, useRef, useEffect } from "react";

interface ConsoleEntry {
  id: string;
  type: "input" | "output" | "error" | "info";
  text: string;
  timestamp: string;
}

export function SandboxConsole({
  entries,
  onCommand,
  extensionName,
}: {
  entries: ConsoleEntry[];
  onCommand?: (command: string) => void;
  extensionName: string;
}) {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current && scrollRef.current.scrollTo) { scrollRef.current.scrollTo(0, scrollRef.current.scrollHeight); }
  }, [entries]);

  const handleSubmit = () => {
    if (!input.trim()) return;
    setHistory((prev) => [...prev, input]);
    setHistoryIndex(-1);
    onCommand?.(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSubmit();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length > 0) {
        const newIdx = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIdx);
        setInput(history[newIdx]);
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex >= 0) {
        const newIdx = historyIndex + 1;
        if (newIdx >= history.length) {
          setHistoryIndex(-1);
          setInput("");
        } else {
          setHistoryIndex(newIdx);
          setInput(history[newIdx]);
        }
      }
    }
  };

  const typeColors: Record<string, string> = {
    input: "text-cyan-400",
    output: "text-green-400",
    error: "text-red-400",
    info: "text-yellow-400",
  };

  const typePrefix: Record<string, string> = {
    input: "›",
    output: "←",
    error: "✗",
    info: "ℹ",
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
          </div>
          <span className="text-xs text-gray-400 ml-2">🔲 {extensionName} — Sandbox Console</span>
        </div>
        <span className="text-xs text-gray-500">{entries.length} entries</span>
      </div>

      <div ref={scrollRef} className="bg-gray-900 p-3 h-64 overflow-y-auto font-mono text-xs space-y-0.5">
        {entries.map((entry) => (
          <div key={entry.id} className="flex gap-2">
            <span className="text-gray-600 shrink-0 w-16">{entry.timestamp}</span>
            <span className={`shrink-0 ${typeColors[entry.type]}`}>{typePrefix[entry.type]}</span>
            <span className={typeColors[entry.type]}>{entry.text}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="text-gray-600">Type a command to get started...</div>
        )}
      </div>

      <div className="bg-gray-800 px-3 py-2 flex items-center gap-2">
        <span className="text-cyan-400 font-mono text-sm">›</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command..."
          className="flex-1 bg-transparent border-none outline-none text-white text-sm font-mono placeholder-gray-600"
        />
      </div>
    </div>
  );
}

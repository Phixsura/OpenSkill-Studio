"use client";

interface DiffLine { type: string; line: number; content: string; }
interface DiffViewerProps { lines: DiffLine[]; added: number; removed: number; summary: string; }

const LINE_STYLE: Record<string, string> = {
  added: "bg-green-50 dark:bg-green-900/10 text-green-700 dark:text-green-400",
  removed: "bg-red-50 dark:bg-red-900/10 text-red-700 dark:text-red-400 line-through",
  unchanged: "",
};
const PREFIX: Record<string, string> = { added: "+", removed: "-", unchanged: " " };

export function DiffViewer({ lines, added, removed, summary }: DiffViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <span className="text-xs font-mono">{summary}</span>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">+{added}</span>
          <span className="text-red-500">-{removed}</span>
        </div>
      </div>
      <div className="font-mono text-xs overflow-auto max-h-96">
        {lines.map((l, i) => (
          <div key={i} className={`flex px-3 py-0.5 ${LINE_STYLE[l.type] || ""}`}>
            <span className="text-gray-400 w-8 shrink-0 select-none text-right mr-2">{l.line}</span>
            <span className="text-gray-400 w-3 shrink-0">{PREFIX[l.type]}</span>
            <span className="flex-1">{l.content}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

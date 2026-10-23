"use client";

interface DiffLine { content: string; type: "add" | "remove" | "context"; }
interface DiffHunk { header: string; lines: DiffLine[]; }
interface DiffViewerProps { hunks: DiffHunk[]; additions: number; removals: number; }

const lineColors: Record<string, string> = {
  add: "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-300",
  remove: "bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-300",
  context: "",
};

export function DiffViewer({ hunks, additions, removals }: DiffViewerProps) {
  return (
    <div className="rounded-lg border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center gap-3 border-b bg-gray-50 px-4 py-2 text-xs dark:bg-gray-900 dark:border-gray-700">
        <span className="text-green-600">+{additions}</span>
        <span className="text-red-600">-{removals}</span>
      </div>
      {hunks.map((hunk, hi) => (
        <div key={hi}>
          <div className="bg-blue-50 px-4 py-1 text-xs font-mono text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">{hunk.header}</div>
          {hunk.lines.map((line, li) => (
            <pre key={li} className={`px-4 py-0.5 text-xs font-mono ${lineColors[line.type]}`}>{line.content}</pre>
          ))}
        </div>
      ))}
    </div>
  );
}

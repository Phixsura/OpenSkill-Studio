"use client";

import { useState } from "react";

export function ExtensionMarkdownPreview({
  source,
  extensionName,
  onSave,
}: {
  source: string;
  extensionName: string;
  onSave?: (content: string) => void;
}) {
  const [content, setContent] = useState(source);
  const [mode, setMode] = useState<"edit" | "preview" | "split">("split");

  const renderMarkdown = (md: string) => {
    // Simple markdown rendering
    return md
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-5 mb-2">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-6 mb-3">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 rounded text-sm">$1</code>')
      .replace(/^- (.+)$/gm, '<li class="ml-4">• $1</li>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 flex items-center justify-between border-b dark:border-gray-700">
        <span className="text-sm font-semibold">📝 {extensionName} README</span>
        <div className="flex gap-1">
          {(["edit", "split", "preview"] as const).map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`text-xs px-2 py-1 rounded ${mode === m ? "bg-blue-600 text-white" : "text-gray-500"}`}>
              {m === "edit" ? "✏️ Edit" : m === "preview" ? "👁️ Preview" : "⬛ Split"}
            </button>
          ))}
        </div>
      </div>

      <div className={`flex ${mode === "split" ? "divide-x dark:divide-gray-700" : ""}`}>
        {(mode === "edit" || mode === "split") && (
          <div className={mode === "split" ? "w-1/2" : "w-full"}>
            <textarea value={content} onChange={(e) => setContent(e.target.value)}
              className="w-full h-64 p-4 bg-white dark:bg-gray-900 text-sm font-mono resize-none outline-none"
              placeholder="Write markdown..." />
          </div>
        )}
        {(mode === "preview" || mode === "split") && (
          <div className={`${mode === "split" ? "w-1/2" : "w-full"} p-4 h-64 overflow-y-auto`}>
            <div className="prose dark:prose-invert text-sm"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }} />
          </div>
        )}
      </div>

      {onSave && (
        <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 border-t dark:border-gray-700">
          <button onClick={() => onSave(content)}
            className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg">
            💾 Save
          </button>
        </div>
      )}
    </div>
  );
}

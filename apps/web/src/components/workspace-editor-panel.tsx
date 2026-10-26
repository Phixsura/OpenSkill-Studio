"use client";

import { useState } from "react";

interface WorkspaceFile {
  path: string;
  language: string;
  size: number;
}

interface Workspace {
  id: string;
  name: string;
  status: "active" | "archived" | "building" | "error";
  fileCount: number;
  collaborators: string[];
  owner: string;
}

const langIcons: Record<string, string> = {
  typescript: "📘", javascript: "📜", python: "🐍", json: "📋",
  markdown: "📝", yaml: "⚙️", text: "📄",
};

const statusConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢" },
  archived: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", icon: "📦" },
  building: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔨" },
  error: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
};

export function WorkspaceEditorPanel({
  workspace,
  files,
  selectedFile,
  fileContent,
  onSelectFile,
  onSave,
  onAddCollaborator,
}: {
  workspace: Workspace;
  files: WorkspaceFile[];
  selectedFile: string | null;
  fileContent: string;
  onSelectFile?: (path: string) => void;
  onSave?: (path: string, content: string) => void;
  onAddCollaborator?: (userId: string) => void;
}) {
  const [content, setContent] = useState(fileContent);
  const cfg = statusConfig[workspace.status];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">{workspace.name}</h2>
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.icon} {workspace.status}</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <span>👤 {workspace.owner}</span>
          {workspace.collaborators.length > 0 && (
            <span>+ {workspace.collaborators.length} collaborators</span>
          )}
        </div>
      </div>

      <div className="flex gap-3 h-80">
        {/* File tree */}
        <div className="w-48 shrink-0 rounded-lg border dark:border-gray-700 overflow-y-auto p-1">
          {files.map((f) => (
            <div key={f.path}
              onClick={() => { onSelectFile?.(f.path); setContent(fileContent); }}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs cursor-pointer ${
                selectedFile === f.path ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700" : "hover:bg-gray-100 dark:hover:bg-gray-800"
              }`}>
              <span>{langIcons[f.language] || "📄"}</span>
              <span className="truncate">{f.path}</span>
            </div>
          ))}
        </div>

        {/* Editor */}
        <div className="flex-1 flex flex-col">
          {selectedFile ? (
            <>
              <div className="flex items-center justify-between mb-1">
                <code className="text-xs text-gray-500">{selectedFile}</code>
                <button onClick={() => onSave?.(selectedFile, content)}
                  className="text-xs bg-green-600 text-white px-3 py-1 rounded">Save</button>
              </div>
              <textarea value={content} onChange={(e) => setContent(e.target.value)}
                className="flex-1 rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 text-xs font-mono text-green-400 resize-none" />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-sm text-gray-500">
              Select a file to edit
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

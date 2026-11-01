"use client";
import { useState } from "react";

interface CliCmd { name: string; description: string; usage: string; }
interface CliTool { toolId: string; name: string; version: string; installCmd: string; commands: CliCmd[]; }

export function CliToolCard({ tool }: { tool: CliTool }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="border dark:border-gray-700 rounded-xl overflow-hidden">
      <button onClick={() => setExpanded(!expanded)} className="w-full text-left p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-lg">⌨️</span>
          <div>
            <span className="font-bold text-sm">{tool.name}</span>
            <span className="text-xs text-gray-500 ml-2">v{tool.version}</span>
          </div>
        </div>
        <span className="text-xs text-gray-400">{tool.commands.length} commands {expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && (
        <div className="border-t dark:border-gray-700 p-4 space-y-2 bg-gray-50 dark:bg-gray-800/50">
          {tool.installCmd && (
            <div className="font-mono text-xs bg-black text-green-400 rounded-lg p-2">$ {tool.installCmd}</div>
          )}
          {tool.commands.map(cmd => (
            <div key={cmd.name} className="text-sm">
              <code className="text-xs font-mono text-blue-600 dark:text-blue-400">{cmd.usage}</code>
              <span className="text-xs text-gray-500 ml-2">— {cmd.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

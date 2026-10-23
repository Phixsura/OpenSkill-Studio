"use client";

interface SlackPreviewProps { text: string; channel: string; hasBlocks: boolean; }

export function SlackPreview({ text, channel, hasBlocks }: SlackPreviewProps) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm dark:bg-gray-900 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-8 w-8 rounded bg-purple-600 flex items-center justify-center text-white text-sm font-bold">O</div>
        <div>
          <p className="text-sm font-bold">OpenSkill Bot</p>
          <p className="text-xs text-gray-400">{channel || "#notifications"}</p>
        </div>
      </div>
      <div className="border-l-4 border-blue-500 pl-3">
        <p className="text-sm whitespace-pre-wrap">{text}</p>
      </div>
      {hasBlocks && <p className="mt-2 text-xs text-gray-400 italic">+ rich blocks attached</p>}
    </div>
  );
}

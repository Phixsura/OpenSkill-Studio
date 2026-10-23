"use client";

import { useState } from "react";

interface TruncatedTextProps { text: string; fullText: string; truncated: boolean; }

export function TruncatedText({ text, fullText, truncated }: TruncatedTextProps) {
  const [expanded, setExpanded] = useState(false);
  return (
    <span>
      <span>{expanded ? fullText : text}</span>
      {truncated && (
        <button onClick={() => setExpanded(!expanded)}
          className="ml-1 text-xs text-blue-500 hover:underline">
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </span>
  );
}

"use client";
import { useState } from "react";

interface ShareButtonsProps { twitter: string; linkedin: string;
  copyUrl: string; title: string; }

export function ShareButtons({ twitter, linkedin, copyUrl, title }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(copyUrl).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400">Share:</span>
      <a href={twitter} target="_blank" rel="noopener noreferrer"
        className="text-xs px-2 py-1 rounded bg-blue-400 text-white hover:bg-blue-500">Twitter</a>
      <a href={linkedin} target="_blank" rel="noopener noreferrer"
        className="text-xs px-2 py-1 rounded bg-blue-700 text-white hover:bg-blue-800">LinkedIn</a>
      <button onClick={handleCopy}
        className="text-xs px-2 py-1 rounded border hover:bg-gray-50 dark:hover:bg-gray-800">
        {copied ? "✓ Copied" : "🔗 Copy"}
      </button>
    </div>
  );
}

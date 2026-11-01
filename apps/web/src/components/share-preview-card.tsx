"use client";
import { useState } from "react";

interface SharePreviewCardProps { title: string; description: string; url: string;
  image: string; twitterLink: string; linkedinLink: string; }

export function SharePreviewCard({ title, description, url, image, twitterLink, linkedinLink }: SharePreviewCardProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(url).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-sm">
      <div className="bg-gray-100 dark:bg-gray-800 h-32 flex items-center justify-center text-4xl">📱</div>
      <div className="p-4">
        <h4 className="text-sm font-bold mb-1">{title}</h4>
        <p className="text-xs text-gray-500 mb-3">{description}</p>
        <div className="flex gap-1.5">
          <a href={twitterLink} target="_blank" rel="noopener noreferrer"
            className="text-xs px-2.5 py-1 bg-blue-400 text-white rounded hover:bg-blue-500">Twitter</a>
          <a href={linkedinLink} target="_blank" rel="noopener noreferrer"
            className="text-xs px-2.5 py-1 bg-blue-700 text-white rounded hover:bg-blue-800">LinkedIn</a>
          <button onClick={handleCopy}
            className="text-xs px-2.5 py-1 border rounded hover:bg-gray-50 dark:hover:bg-gray-800">
            {copied ? "✓ Copied" : "🔗 Copy"}
          </button>
        </div>
      </div>
    </div>
  );
}

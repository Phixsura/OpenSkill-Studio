"use client";

import { useState } from "react";

interface ShareButtonsProps { url: string; twitter: string; linkedin: string; email: string; copyText: string; }

export function ShareButtons({ url, twitter, linkedin, email, copyText }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard?.writeText(copyText); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div className="flex gap-2">
      <a href={twitter} target="_blank" rel="noopener noreferrer" className="rounded border px-2 py-1 text-xs hover:bg-gray-100">𝕏 Tweet</a>
      <a href={linkedin} target="_blank" rel="noopener noreferrer" className="rounded border px-2 py-1 text-xs hover:bg-gray-100">in Share</a>
      <a href={email} className="rounded border px-2 py-1 text-xs hover:bg-gray-100">✉️ Email</a>
      <button onClick={copy} className="rounded border px-2 py-1 text-xs hover:bg-gray-100">{copied ? "✅" : "📋 Copy"}</button>
    </div>
  );
}

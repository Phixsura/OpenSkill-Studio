"use client";

import { useState } from "react";

interface QuickstartCodeProps { pythonCode: string; typescriptCode: string; }

export function QuickstartCode({ pythonCode, typescriptCode }: QuickstartCodeProps) {
  const [lang, setLang] = useState<"python" | "typescript">("python");
  return (
    <div>
      <div className="mb-2 flex gap-2">
        <button onClick={() => setLang("python")} className={`rounded px-3 py-1 text-xs ${lang === "python" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>🐍 Python</button>
        <button onClick={() => setLang("typescript")} className={`rounded px-3 py-1 text-xs ${lang === "typescript" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>🟦 TypeScript</button>
      </div>
      <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm text-green-400"><code>{lang === "python" ? pythonCode : typescriptCode}</code></pre>
    </div>
  );
}

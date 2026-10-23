"use client";

interface Section { key: string; title: string; icon: string; email?: string; url?: string; response_time?: string; items?: { question: string; answer: string }[]; }
interface SupportPageLayoutProps { appName: string; sections: Section[]; }

function safeUrl(u?: string): string | undefined {
  if (!u) return undefined;
  if (u.startsWith("/") && !u.startsWith("//")) return u;
  try { const p = new URL(u); return ["http:", "https:"].includes(p.protocol) ? u : undefined; } catch { return undefined; }
}

export function SupportPageLayout({ appName, sections }: SupportPageLayoutProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{appName} Support</h1>
      {sections.map(s => (
        <div key={s.key} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <h2 className="flex items-center gap-2 text-lg font-semibold">{s.icon} {s.title}</h2>
          {s.key === "faq" && s.items && (
            <div className="mt-3 space-y-2">
              {s.items.map((f, i) => (
                <details key={i} className="rounded border p-2 dark:border-gray-700">
                  <summary className="cursor-pointer text-sm font-medium">{f.question}</summary>
                  <p className="mt-1 text-sm text-gray-500">{f.answer}</p>
                </details>
              ))}
            </div>
          )}
          {safeUrl(s.url) && <a href={safeUrl(s.url)} rel="noopener noreferrer" target="_blank" className="mt-2 inline-block text-sm text-blue-600 hover:underline">Visit →</a>}
          {s.email && (
            <div className="mt-2">
              <a href={`mailto:${s.email}`} className="text-sm text-blue-600">{s.email}</a>
              {s.response_time && <p className="text-xs text-gray-400">Response time: {s.response_time}</p>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

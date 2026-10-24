"use client";

interface NewsletterSection { type: string; title: string; body: string; cta: string; link: string; }
interface NewsletterPreviewProps { subject: string; sections: NewsletterSection[];
  readTimeMin: number; footer: string; }

export function NewsletterPreview({ subject, sections, readTimeMin, footer }: NewsletterPreviewProps) {
  return (
    <div className="max-w-lg mx-auto rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-blue-600 text-white p-4 text-center">
        <p className="text-xs opacity-75">Newsletter Preview</p>
        <h2 className="text-lg font-bold">{subject}</h2>
        <p className="text-xs opacity-75">{readTimeMin} min read</p>
      </div>
      <div className="p-5 space-y-4 bg-white dark:bg-gray-900">
        {sections.map((s, i) => (
          <div key={i}>
            <h3 className="font-semibold mb-1">{s.title}</h3>
            <p className="text-sm text-gray-500">{s.body}</p>
            {s.cta && <p className="text-sm text-blue-600 mt-1 font-medium">{s.cta} →</p>}
          </div>
        ))}
      </div>
      <div className="px-5 py-3 bg-gray-50 dark:bg-gray-800 text-xs text-gray-400 text-center">{footer}</div>
    </div>
  );
}

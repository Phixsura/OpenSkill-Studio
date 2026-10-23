"use client";

interface Section { heading: string; body: string; cta_label?: string; cta_url?: string; }
interface NewsletterPreviewProps { title: string; edition: number; sections: Section[];
  onSend: () => void; onEdit: () => void; }

export function NewsletterPreview({ title, edition, sections, onSend, onEdit }: NewsletterPreviewProps) {
  return (
    <div className="mx-auto max-w-lg space-y-4">
      <div className="rounded-t-xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-center text-white">
        <p className="text-xs opacity-60">Edition #{edition}</p>
        <h1 className="mt-1 text-2xl font-bold">{title}</h1>
      </div>
      <div className="space-y-4 px-4">
        {sections.map((s, i) => (
          <div key={i} className="border-b pb-4 dark:border-gray-700">
            <h2 className="font-bold">{s.heading}</h2>
            <p className="mt-1 text-sm text-gray-500">{s.body}</p>
            {s.cta_label && s.cta_url && (
              <a href={s.cta_url} className="mt-2 inline-block text-sm text-blue-600 hover:underline">
                {s.cta_label} →
              </a>
            )}
          </div>
        ))}
      </div>
      <div className="flex gap-2 px-4 pb-4">
        <button onClick={onEdit} className="flex-1 rounded border py-2 text-sm dark:border-gray-600">Edit</button>
        <button onClick={onSend} className="flex-1 rounded bg-blue-600 py-2 text-sm text-white">Send Newsletter</button>
      </div>
    </div>
  );
}

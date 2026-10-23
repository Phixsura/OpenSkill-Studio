"use client";

interface Cta { label: string; url: string; }
interface Announcement { announcement_id: string; title: string; body: string;
  feature_tag: string; cta: Cta | null; published_at: string; }
interface FeatureAnnouncementCardProps { announcements: Announcement[];
  onDismiss: (id: string) => void; onCtaClick: (url: string) => void; }

export function FeatureAnnouncementCard({ announcements, onDismiss, onCtaClick }: FeatureAnnouncementCardProps) {
  if (announcements.length === 0) return null;
  return (
    <div className="space-y-3">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        ✨ What&apos;s New
        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">{announcements.length}</span>
      </h2>
      {announcements.map(a => (
        <div key={a.announcement_id} className="rounded-lg border border-blue-200 bg-blue-50/50 p-4 dark:border-blue-800 dark:bg-blue-900/10">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{a.title}</h3>
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900/30">{a.feature_tag}</span>
              </div>
              <p className="mt-1 text-sm text-gray-500">{a.body}</p>
            </div>
            <button onClick={() => onDismiss(a.announcement_id)} className="text-xs text-gray-400">✕</button>
          </div>
          {a.cta && (
            <button onClick={() => onCtaClick(a.cta!.url)}
              className="mt-2 rounded bg-blue-600 px-3 py-1 text-xs text-white">{a.cta.label}</button>
          )}
        </div>
      ))}
    </div>
  );
}

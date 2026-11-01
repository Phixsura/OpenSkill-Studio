"use client";

interface SupportChannel { type: string; icon: string; value: string; }
interface SupportContactCardProps { developer: string; responseTime: string;
  channels: SupportChannel[]; docsUrl: string; }

export function SupportContactCard({ developer, responseTime, channels, docsUrl }: SupportContactCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-1">💬 Support</h3>
      <p className="text-xs text-gray-400 mb-3">By {developer} · Response: {responseTime}</p>
      <div className="space-y-2 mb-3">
        {channels.map(c => (
          <div key={c.type} className="flex items-center gap-2 text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <span>{c.icon}</span><span>{c.value}</span>
          </div>
        ))}
      </div>
      {docsUrl && (
        <a href={docsUrl} target="_blank" rel="noopener noreferrer"
          className="block text-center text-sm text-blue-600 hover:text-blue-700">📚 View Documentation</a>
      )}
    </div>
  );
}

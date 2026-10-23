"use client";

interface NotificationPreviewCardProps { emoji: string; title: string;
  message: string; color: string; service?: string; channel: string; }

export function NotificationPreviewCard({ emoji, title, message, color, service, channel }: NotificationPreviewCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 border-b dark:border-gray-700">
        <span className="text-xs text-gray-400">Preview: #{channel}</span>
      </div>
      <div className="flex">
        <div className="w-1 shrink-0" style={{ backgroundColor: color }} />
        <div className="p-4 flex-1">
          <p className="text-sm font-bold mb-1">{emoji} {title}</p>
          <p className="text-sm text-gray-600 dark:text-gray-300">{message}</p>
          {service && (
            <p className="text-xs text-gray-400 mt-2">Service: <strong>{service}</strong></p>
          )}
        </div>
      </div>
    </div>
  );
}

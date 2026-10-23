"use client";

interface Avatar { name: string; initials: string; avatar_url: string; }
interface AvatarStackProps { avatars: Avatar[]; overflowText: string | null; }

export function AvatarStack({ avatars, overflowText }: AvatarStackProps) {
  return (
    <div className="flex items-center -space-x-2">
      {avatars.map((a, i) => (
        <div key={i} title={a.name}
          className="relative h-8 w-8 rounded-full border-2 border-white dark:border-gray-900 overflow-hidden bg-gray-200 dark:bg-gray-700"
          style={{ zIndex: avatars.length - i }}>
          <img src={a.avatar_url} alt={a.name} className="h-full w-full object-cover"
            onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-300">
            {a.initials}
          </span>
        </div>
      ))}
      {overflowText && (
        <div className="relative flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gray-100 text-xs font-medium dark:border-gray-900 dark:bg-gray-800">
          {overflowText}
        </div>
      )}
    </div>
  );
}

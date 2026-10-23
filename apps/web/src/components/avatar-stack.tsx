"use client";

interface Avatar { name: string; initials: string; color: string; image: string | null; }
interface AvatarStackProps { avatars: Avatar[]; remaining: number; showRemaining: boolean;
  remainingLabel: string; size?: number; }

export function AvatarStack({ avatars, remaining, showRemaining, remainingLabel, size = 32 }: AvatarStackProps) {
  return (
    <div className="flex items-center -space-x-2">
      {avatars.map((a, i) => (
        <div key={i} className="relative rounded-full border-2 border-white dark:border-gray-900"
          style={{ width: size, height: size, zIndex: avatars.length - i }}
          title={a.name}>
          {a.image ? (
            <img src={a.image} alt={a.name} className="h-full w-full rounded-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center rounded-full text-xs font-bold text-white"
              style={{ backgroundColor: a.color, fontSize: size * 0.35 }}>
              {a.initials}
            </div>
          )}
        </div>
      ))}
      {showRemaining && (
        <div className="relative flex items-center justify-center rounded-full border-2 border-white bg-gray-200 text-xs font-bold text-gray-600 dark:border-gray-900 dark:bg-gray-700 dark:text-gray-300"
          style={{ width: size, height: size, zIndex: 0 }}>
          {remainingLabel}
        </div>
      )}
    </div>
  );
}

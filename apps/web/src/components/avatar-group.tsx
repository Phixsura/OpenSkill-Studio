"use client";

interface AvatarData { initials: string; bgColor: string; }
interface AvatarGroupProps { avatars: AvatarData[]; size?: number;
  remaining: number; remainingDisplay: string; }

export function AvatarGroup({ avatars, size = 32, remaining, remainingDisplay }: AvatarGroupProps) {
  return (
    <div className="flex items-center -space-x-2">
      {avatars.map((a, i) => (
        <div key={i} className="rounded-full border-2 border-white dark:border-gray-900 flex items-center justify-center text-white text-xs font-bold"
             style={{ width: size, height: size, backgroundColor: a.bgColor, zIndex: avatars.length - i }}>
          {a.initials}
        </div>
      ))}
      {remaining > 0 && (
        <div className="rounded-full border-2 border-white dark:border-gray-900 bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-medium text-gray-600"
             style={{ width: size, height: size }}>
          {remainingDisplay}
        </div>
      )}
    </div>
  );
}

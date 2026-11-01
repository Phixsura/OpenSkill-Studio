"use client";

interface AvatarDisplayProps { initials: string; bgColor: string; textColor: string;
  size: number; fontSize: number; imageUrl?: string; }

export function AvatarDisplay({ initials, bgColor, textColor, size, fontSize, imageUrl }: AvatarDisplayProps) {
  if (imageUrl) {
    return (
      <div className="overflow-hidden rounded-full" style={{ width: size, height: size }}>
        <img src={imageUrl} alt={initials} className="h-full w-full object-cover" />
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center rounded-full font-bold"
      style={{ width: size, height: size, backgroundColor: bgColor,
               color: textColor, fontSize }}>
      {initials}
    </div>
  );
}

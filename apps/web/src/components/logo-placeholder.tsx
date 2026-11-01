"use client";

interface LogoPlaceholderProps { initials: string; gradient: string; size: number;
  fontSize: number; shape: string; imageUrl?: string; }

export function LogoPlaceholder({ initials, gradient, size, fontSize, shape, imageUrl }: LogoPlaceholderProps) {
  if (imageUrl) {
    return (
      <div className={`overflow-hidden ${shape}`} style={{ width: size, height: size }}>
        <img src={imageUrl} alt={initials} className="h-full w-full object-cover" />
      </div>
    );
  }
  return (
    <div className={`flex items-center justify-center bg-gradient-to-br ${gradient} ${shape} font-bold text-white`}
      style={{ width: size, height: size, fontSize }}>
      {initials}
    </div>
  );
}

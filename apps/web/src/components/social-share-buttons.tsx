"use client";

interface SocialShareButtonsProps { url: string; title: string; description: string; }

export function SocialShareButtons({ url, title, description }: SocialShareButtonsProps) {
  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);
  const encodedDesc = encodeURIComponent(description);

  const platforms = [
    { name: "Twitter", icon: "𝕏", href: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`, color: "hover:bg-black hover:text-white" },
    { name: "LinkedIn", icon: "in", href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`, color: "hover:bg-blue-700 hover:text-white" },
    { name: "Reddit", icon: "📮", href: `https://reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`, color: "hover:bg-orange-600 hover:text-white" },
    { name: "Email", icon: "📧", href: `mailto:?subject=${encodedTitle}&body=${encodedDesc}%20${encodedUrl}`, color: "hover:bg-gray-600 hover:text-white" },
  ];

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400">Share:</span>
      {platforms.map(p => (
        <a key={p.name} href={p.href} target="_blank" rel="noopener noreferrer"
          title={`Share on ${p.name}`}
          className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs dark:border-gray-600 ${p.color}`}>
          {p.icon}
        </a>
      ))}
    </div>
  );
}

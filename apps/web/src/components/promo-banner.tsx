"use client";

interface PromoBannerProps { title: string; body: string; cta: string;
  gradient: string; icon: string; onClick: () => void; onDismiss: () => void; }

export function PromoBanner({ title, body, cta, gradient, icon, onClick, onDismiss }: PromoBannerProps) {
  return (
    <div className={`rounded-2xl bg-gradient-to-r ${gradient} p-6 text-white relative`}>
      <button onClick={onDismiss} className="absolute top-3 right-3 text-white/60 hover:text-white text-sm">✕</button>
      <div className="flex items-center gap-4">
        <span className="text-4xl">{icon}</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold">{title}</h3>
          <p className="text-sm opacity-90">{body}</p>
        </div>
        <button onClick={onClick}
          className="px-5 py-2 bg-white text-gray-900 rounded-lg text-sm font-medium hover:bg-gray-100 shrink-0">{cta}</button>
      </div>
    </div>
  );
}

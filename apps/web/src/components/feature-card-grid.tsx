"use client";

interface FeatureCard { title: string; description: string; icon: string; category: string; link: string | null; }
interface FeatureCardGridProps { cards: FeatureCard[]; onCardClick?: (title: string) => void; }

export function FeatureCardGrid({ cards, onCardClick }: FeatureCardGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map(card => (
        <div key={card.title} className="rounded-xl border p-5 hover:shadow-md dark:border-gray-700"
          onClick={() => onCardClick?.(card.title)} role={onCardClick ? "button" : undefined}>
          <span className="text-3xl">{card.icon}</span>
          <h3 className="mt-3 text-lg font-bold">{card.title}</h3>
          <p className="mt-1 text-sm text-gray-500">{card.description}</p>
          <span className="mt-2 inline-block rounded bg-gray-100 px-2 py-0.5 text-[10px] capitalize dark:bg-gray-800">
            {card.category}
          </span>
        </div>
      ))}
    </div>
  );
}

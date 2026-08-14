import type { Metadata } from "next";
import { notFound } from "next/navigation";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || "http://localhost:8000";

interface ItemDetail {
  slug: string;
  title: string;
  description: string | null;
  tags: string[];
  external_url: string | null;
  score: number | null;
  show_score: boolean;
  source_org_name: string | null;
  source_project: string | null;
}

async function fetchItem(username: string, slug: string): Promise<ItemDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/u/${username}/items/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    const data = await res.json();
    return data.data;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ username: string; itemSlug: string }> }): Promise<Metadata> {
  const { username, itemSlug } = await params;
  const item = await fetchItem(username, itemSlug);
  if (!item) return { title: "Not Found" };
  return {
    title: `${item.title} | OpenSkill Studio`,
    description: item.description?.slice(0, 160),
  };
}

export default async function PublicItemPage({ params }: { params: Promise<{ username: string; itemSlug: string }> }) {
  const { username, itemSlug } = await params;
  const item = await fetchItem(username, itemSlug);
  if (!item) notFound();

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold">{item.title}</h1>
      {item.source_org_name && (
        <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
          Completed at {item.source_org_name}{item.source_project && ` / ${item.source_project}`}
        </p>
      )}
      {item.show_score && item.score != null && (
        <p className="mt-2 text-lg font-bold">⭐ {item.score}/100</p>
      )}
      <div className="mt-4 flex flex-wrap gap-2">
        {item.tags.map((tag) => (
          <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-3 py-1 text-sm">{tag}</span>
        ))}
      </div>
      {item.description && (
        <div className="prose prose-sm mt-6 max-w-none dark:prose-invert">
          <p>{item.description}</p>
        </div>
      )}
      {item.external_url && (
        <a href={item.external_url} target="_blank" rel="noopener noreferrer"
          className="mt-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline">
          View Project →
        </a>
      )}
      <div className="mt-8">
        <a href={`/u/${username}`} className="text-sm text-[hsl(var(--primary))] hover:underline">← Back to profile</a>
      </div>
    </main>
  );
}

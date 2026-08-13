import type { Metadata } from "next";
import { notFound } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface PublicProfile {
  username: string;
  display_name: string;
  headline: string | null;
  bio: string | null;
  avatar_url: string | null;
  location: string | null;
  website_url: string | null;
  social_links: Record<string, string>;
  skills: { name: string; category: string; completion_pct: number; completed: boolean }[];
  featured_items: { slug: string; title: string; description: string | null; cover_image_url: string | null; tags: string[]; score: number | null; show_score: boolean; source_org_name: string | null }[];
  item_count: number;
  joined_at: string;
}

async function fetchProfile(username: string): Promise<PublicProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/u/${username}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ username: string }> }): Promise<Metadata> {
  const { username } = await params;
  const profile = await fetchProfile(username);
  if (!profile) return { title: "Not Found" };
  return {
    title: `${profile.display_name} | OpenSkill Studio`,
    description: profile.headline || profile.bio?.slice(0, 160),
    openGraph: {
      title: `${profile.display_name} — ${profile.headline ?? ""}`,
      url: `https://openskill.studio/u/${profile.username}`,
      type: "profile",
    },
  };
}

export default async function PublicProfilePage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params;
  const profile = await fetchProfile(username);
  if (!profile) notFound();

  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Person",
            name: profile.display_name,
            url: `https://openskill.studio/u/${profile.username}`,
            image: profile.avatar_url,
            jobTitle: profile.headline,
            sameAs: Object.values(profile.social_links || {}).filter(
              (u) => typeof u === "string" && /^https?:\/\//i.test(u),
            ),
          })
            .replace(/</g, "\\u003c")
            .replace(/>/g, "\\u003e")
            .replace(/&/g, "\\u0026"),
        }}
      />

      <div className="flex items-start gap-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-2xl font-bold">
          {profile.display_name[0]}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{profile.display_name}</h1>
          {profile.headline && <p className="text-lg text-[hsl(var(--muted-foreground))]">{profile.headline}</p>}
          {profile.location && <p className="text-sm text-[hsl(var(--muted-foreground))]">{profile.location}</p>}
          <div className="mt-2 flex gap-3">
            {Object.entries(profile.social_links)
              .filter(([, url]) => typeof url === "string" && /^https?:\/\//i.test(url))
              .map(([platform, url]) => (
              <a key={platform} href={url} target="_blank" rel="noopener noreferrer"
                className="text-sm capitalize text-[hsl(var(--primary))] hover:underline">{platform}</a>
            ))}
          </div>
        </div>
      </div>

      {profile.skills.length > 0 && (
        <section className="mt-8">
          <h2 className="text-lg font-semibold mb-3">Skills</h2>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((s) => (
              <span key={s.name} className={`rounded-full px-3 py-1 text-sm font-medium ${
                s.completed ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"}`}>
                {s.completed ? "✓" : `${s.completion_pct}%`} {s.name}
              </span>
            ))}
          </div>
        </section>
      )}

      {profile.featured_items.length > 0 && (
        <section className="mt-8">
          <h2 className="text-lg font-semibold mb-3">Featured Projects</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {profile.featured_items.map((item) => (
              <a key={item.slug} href={`/u/${profile.username}/${item.slug}`}
                className="group block overflow-hidden rounded-lg border transition-shadow hover:shadow-md">
                <div className="aspect-video w-full bg-[hsl(var(--secondary))] flex items-center justify-center">
                  <span className="text-4xl">🎨</span>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">{item.title}</h3>
                  {item.show_score && item.score != null && (
                    <span className="text-sm text-[hsl(var(--muted-foreground))]">⭐ {item.score}/100</span>
                  )}
                  <div className="mt-2 flex flex-wrap gap-1">
                    {item.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">{tag}</span>
                    ))}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </section>
      )}

      {profile.bio && (
        <section className="mt-8">
          <h2 className="text-lg font-semibold mb-3">About</h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">{profile.bio}</p>
        </section>
      )}

      <footer className="mt-12 text-center text-xs text-[hsl(var(--muted-foreground))]">
        ⚡ Powered by OpenSkill Studio
      </footer>
    </main>
  );
}

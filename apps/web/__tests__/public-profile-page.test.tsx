/**
 * Server-component test: PublicProfilePage is an async RSC — invoke it with
 * mocked global fetch and render the returned JSX.
 */
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const notFound = vi.hoisted(() =>
  vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
);
vi.mock("next/navigation", () => ({ notFound }));

import PublicProfilePage, { generateMetadata } from "@/app/u/[username]/page";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

const PROFILE = {
  username: "ada",
  display_name: "Ada Lovelace",
  headline: "AI artist",
  bio: "I make things",
  avatar_url: null,
  location: "London",
  website_url: null,
  social_links: {
    twitter: "https://x.com/ada",
    evil: "javascript:alert(1)", // must be filtered everywhere
    empty: "",
  },
  skills: [
    { name: "Prompting", category: "ai", completion_pct: 100, completed: true },
    { name: "Compositing", category: "media", completion_pct: 40, completed: false },
  ],
  featured_items: [
    {
      slug: "hero",
      title: "Hero Piece",
      description: null,
      cover_image_url: null,
      tags: ["gen-ai"],
      score: 92,
      show_score: true,
      source_org_name: null,
    },
    {
      slug: "hidden-score",
      title: "Quiet Piece",
      description: null,
      cover_image_url: null,
      tags: [],
      score: 55,
      show_score: false,
      source_org_name: null,
    },
  ],
  item_count: 2,
  joined_at: "2026-01-01T00:00:00Z",
};

function ok(data: unknown) {
  fetchMock.mockResolvedValue({ ok: true, json: () => Promise.resolve({ data }) });
}

beforeEach(() => vi.clearAllMocks());

describe("PublicProfilePage (R479)", () => {
  it("renders profile with scheme-filtered social links (javascript: excluded)", async () => {
    ok(PROFILE);
    render(await PublicProfilePage({ params: Promise.resolve({ username: "ada" }) }));
    expect(screen.getByText("Ada Lovelace")).toBeTruthy();
    expect(screen.getByText("AI artist")).toBeTruthy();
    // http(s)-only filter on visible anchors
    expect(screen.getByText("twitter").closest("a")?.getAttribute("href")).toBe(
      "https://x.com/ada",
    );
    expect(screen.queryByText("evil")).toBeNull();
    expect(screen.queryByText("empty")).toBeNull();
    // JSON-LD sameAs also excludes the javascript: URL
    const ld = document.querySelector('script[type="application/ld+json"]')?.innerHTML ?? "";
    expect(ld).toContain("https://x.com/ada");
    expect(ld).not.toContain("javascript:alert");
    // skills: completed shows check, in-progress shows pct
    expect(screen.getByText(/✓ Prompting/)).toBeTruthy();
    expect(screen.getByText(/40% Compositing/)).toBeTruthy();
  });

  it("score chip only when show_score AND score present; item links slugged", async () => {
    ok(PROFILE);
    render(await PublicProfilePage({ params: Promise.resolve({ username: "ada" }) }));
    const heroCard = screen.getByText("Hero Piece").closest("a");
    expect(heroCard?.textContent).toContain("92/100");
    expect(heroCard?.getAttribute("href")).toBe("/u/ada/hero");
    const quietCard = screen.getByText("Quiet Piece").closest("a");
    expect(quietCard?.textContent).not.toContain("55"); // show_score=false hides it
    expect(screen.getByText("gen-ai")).toBeTruthy(); // tag chip
  });

  it("JSON-LD escapes </script> breakouts", async () => {
    ok({ ...PROFILE, headline: "</script><script>alert(1)</script>" });
    render(await PublicProfilePage({ params: Promise.resolve({ username: "ada" }) }));
    const ld = document.querySelector('script[type="application/ld+json"]')?.innerHTML ?? "";
    expect(ld).not.toContain("</script>");
    expect(ld).toContain("\\u003c"); // < escaped
  });

  it("missing/non-ok profile 404s; fetch rejection also 404s", async () => {
    fetchMock.mockResolvedValue({ ok: false, json: () => Promise.resolve({}) });
    await expect(
      PublicProfilePage({ params: Promise.resolve({ username: "ghost" }) }),
    ).rejects.toThrow("NEXT_NOT_FOUND");

    fetchMock.mockRejectedValue(new Error("network"));
    await expect(
      PublicProfilePage({ params: Promise.resolve({ username: "ghost" }) }),
    ).rejects.toThrow("NEXT_NOT_FOUND");
  });

  it("generateMetadata: title from display name; Not Found fallback", async () => {
    ok(PROFILE);
    const meta = await generateMetadata({ params: Promise.resolve({ username: "ada" }) });
    expect(meta.title).toBe("Ada Lovelace | OpenSkill Studio");
    expect(meta.description).toBe("AI artist");

    fetchMock.mockResolvedValue({ ok: false, json: () => Promise.resolve({}) });
    const nf = await generateMetadata({ params: Promise.resolve({ username: "ghost" }) });
    expect(nf.title).toBe("Not Found");
  });
});

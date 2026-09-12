/** Server-component test for the public portfolio item page. */
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const notFound = vi.hoisted(() =>
  vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
);
vi.mock("next/navigation", () => ({ notFound }));

import PublicItemPage, { generateMetadata } from "@/app/u/[username]/[itemSlug]/page";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

const ITEM = {
  slug: "hero",
  title: "Hero Piece",
  description: "**bold** work",
  tags: ["gen-ai"],
  external_url: "https://demo.example",
  score: 92,
  show_score: true,
  source_org_name: "Acme",
  source_project: "Campaign",
};

const params = Promise.resolve({ username: "ada", itemSlug: "hero" });

function ok(data: unknown) {
  fetchMock.mockResolvedValue({ ok: true, json: () => Promise.resolve({ data }) });
}

beforeEach(() => vi.clearAllMocks());

describe("PublicItemPage (R494)", () => {
  it("renders item with markdown description, provenance line, score, tag, external link", async () => {
    ok(ITEM);
    render(await PublicItemPage({ params }));
    expect(screen.getByText("Hero Piece")).toBeTruthy();
    expect(screen.getByText("Completed at Acme / Campaign")).toBeTruthy();
    expect(screen.getByText("⭐ 92/100")).toBeTruthy();
    expect(screen.getByText("bold").tagName).toBe("STRONG"); // markdown rendered
    expect(screen.getByText("View Project →").closest("a")?.getAttribute("href")).toBe(
      "https://demo.example",
    );
    expect(screen.getByText("← Back to profile").closest("a")?.getAttribute("href")).toBe("/u/ada");
  });

  it("external link is scheme-gated: a javascript: URL renders NO link", async () => {
    ok({ ...ITEM, external_url: "javascript:alert(1)" });
    render(await PublicItemPage({ params }));
    expect(screen.queryByText("View Project →")).toBeNull();
  });

  it("show_score=false hides the score; missing item 404s", async () => {
    ok({ ...ITEM, show_score: false });
    render(await PublicItemPage({ params }));
    expect(screen.queryByText(/92\/100/)).toBeNull();

    fetchMock.mockResolvedValue({ ok: false, json: () => Promise.resolve({}) });
    await expect(PublicItemPage({ params })).rejects.toThrow("NEXT_NOT_FOUND");
  });

  it("generateMetadata: title + truncated description; Not Found fallback", async () => {
    ok(ITEM);
    expect(await generateMetadata({ params })).toEqual({
      title: "Hero Piece | OpenSkill Studio",
      description: "**bold** work",
    });
    fetchMock.mockRejectedValue(new Error("net"));
    expect((await generateMetadata({ params })).title).toBe("Not Found");
  });
});

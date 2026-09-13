import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", skillId: "s-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import SkillDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/skills/[skillId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SKILL = {
  id: "s-1",
  name: "Prompting",
  description: "LLM prompting",
  learning_content: "# Lesson\n\nUse **bold** prompts.",
  difficulty: "beginner",
  estimated_minutes: 45,
  tags: ["ai"],
  prerequisites: [{ id: "s-0", name: "Basics", slug: "basics" }],
};
const EXERCISES = [
  { id: "ex-1", title: "Quiz One", description: "d", type: "multiple_choice", max_score: 10 },
  { id: "ex-2", title: "Free Write", description: "d", type: "free_text", max_score: 20 },
];

function route(skill: unknown = SKILL, exercises: unknown[] = EXERCISES) {
  api.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.endsWith("/exercises")) return Promise.resolve({ data: exercises });
    return Promise.resolve({ data: skill });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("SkillDetailPage (R488)", () => {
  it("renders markdown lesson, numbered exercise rows with humanized type, sidebar details", async () => {
    route();
    render(<SkillDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Prompting");
    // markdown rendered as elements, not literal syntax
    expect(screen.getByRole("heading", { name: "Lesson" })).toBeTruthy();
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    // numbered exercise rows link to exercise pages
    const row1 = screen.getByText("Quiz One").closest("a");
    expect(row1?.getAttribute("href")).toBe("/dashboard/orgs/o-1/skills/s-1/exercises/ex-1");
    expect(row1?.textContent).toContain("1");
    expect(row1?.textContent).toContain("multiple choice · 10 pts"); // underscore humanized
    expect(screen.getByText("Free Write").closest("a")?.textContent).toContain("2");
    // sidebar: difficulty, est time, exercise count, prereq link, tag
    const body = document.body.textContent ?? "";
    expect(body).toContain("45 min");
    expect(screen.getByText("Basics").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/skills/s-0",
    );
    expect(screen.getByText("ai")).toBeTruthy();
  });

  it("null learning_content renders no lesson; zero estimated_minutes row hidden; empty exercises", async () => {
    route(
      { ...SKILL, learning_content: null, estimated_minutes: null, prerequisites: [], tags: [] },
      [],
    );
    render(<SkillDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Prompting");
    expect(screen.queryByRole("heading", { name: "Lesson" })).toBeNull();
    expect(document.body.textContent).not.toContain("Est. time");
    expect(screen.getByText("No exercises yet.")).toBeTruthy();
    expect(screen.queryByText("Prerequisites")).toBeNull();
    expect(screen.queryByText("Tags")).toBeNull();
  });

  it("load failure surfaces the error line", async () => {
    api.mockRejectedValue(new Error("down"));
    render(<SkillDetailPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load skill"));
  });
});

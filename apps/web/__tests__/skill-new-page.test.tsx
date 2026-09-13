import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1" }),
  useRouter: () => ({ replace: nav.replace }),
}));
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import NewSkillPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/skills/new/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const CATS = [{ id: "cat-1", name: "AI Basics" }];

function route(reqs?: { path: string; body?: unknown }[], cats: unknown[] = CATS) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      reqs?.push({ path, body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: { id: "s-new" } });
    }
    if (path.includes("categories")) return Promise.resolve({ data: cats });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

function fillRequired() {
  fireEvent.change(screen.getByLabelText("Skill name"), { target: { value: "Prompting" } });
  fireEvent.change(screen.getByLabelText("Description"), { target: { value: "Learn it" } });
  fireEvent.change(screen.getByLabelText("Category"), { target: { value: "cat-1" } });
}

beforeEach(() => vi.clearAllMocks());

describe("NewSkillPage (R493)", () => {
  it("minimal POST omits blank optionals; tags default to []; redirect to the new skill", async () => {
    const reqs: { path: string; body?: unknown }[] = [];
    route(reqs);
    render(<NewSkillPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "AI Basics" });
    fillRequired();
    fireEvent.click(screen.getByRole("button", { name: "Create Skill" }));
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.body).toEqual({
      name: "Prompting",
      description: "Learn it",
      category_id: "cat-1",
      difficulty: "beginner",
      tags: [],
    });
    expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/o-1/skills/s-new");
  });

  it("tags trimmed + filtered; estimated minutes parsed to int; learning content included when set", async () => {
    const reqs: { path: string; body?: unknown }[] = [];
    route(reqs);
    render(<NewSkillPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "AI Basics" });
    fillRequired();
    fireEvent.change(screen.getByLabelText("Tags"), { target: { value: " ai ,, llm " } });
    fireEvent.change(screen.getByLabelText("Est. minutes"), { target: { value: "45" } });
    fireEvent.change(screen.getByLabelText(/Learning Content/), { target: { value: "# Intro" } });
    fireEvent.change(screen.getByLabelText("Difficulty"), { target: { value: "advanced" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Skill" }));
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.body).toEqual({
      name: "Prompting",
      description: "Learn it",
      category_id: "cat-1",
      difficulty: "advanced",
      tags: ["ai", "llm"],
      estimated_minutes: 45,
      learning_content: "# Intro",
    });
  });

  it("no categories shows the guidance line instead of a select; ApiError verbatim", async () => {
    route(undefined, []);
    const first = render(<NewSkillPage />, { wrapper: wrapper() });
    await first.findByText(/No categories yet/);
    expect(screen.queryByLabelText("Category")).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "POST")
        return Promise.reject(new ApiError(409, "DUP", "Skill name already exists"));
      return Promise.resolve({ data: CATS });
    }) as typeof apiWithAuth);
    render(<NewSkillPage />, { wrapper: wrapper() });
    await screen.findByRole("option", { name: "AI Basics" });
    fillRequired();
    fireEvent.click(screen.getByRole("button", { name: "Create Skill" }));
    expect(await screen.findByText("Skill name already exists")).toBeTruthy();
    expect(nav.replace).not.toHaveBeenCalled();
  });
});

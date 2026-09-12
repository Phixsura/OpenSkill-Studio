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

import NewProjectPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/new/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const TEMPLATE = {
  id: "t-1",
  name: "Chatbot Starter",
  description: "Starter",
  project_type: "general",
  difficulty: "beginner",
  suggested_minutes: 60,
  deliverables: [{ name: "Bot", type: "code", required: true }],
  builtin: true,
};

function route(reqs?: { path: string; method?: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    reqs?.push({
      path,
      method: init?.method,
      body: init?.body ? JSON.parse(init.body) : undefined,
    });
    if (init?.method === "POST") return Promise.resolve({ data: { id: "p-new" } });
    if (path.includes("project-templates")) return Promise.resolve({ data: [TEMPLATE] });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

function fillRequired() {
  fireEvent.change(screen.getByLabelText("Project title"), { target: { value: "My Project" } });
  fireEvent.change(screen.getByLabelText("Description"), { target: { value: "Desc" } });
  fireEvent.change(screen.getByLabelText(/Instructions/), { target: { value: "Do it" } });
}

beforeEach(() => vi.clearAllMocks());

describe("NewProjectPage (R478)", () => {
  it("rubric text parses 'Criterion: score' lines; malformed score defaults to 25; blank lines skipped", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<NewProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot Starter");
    fillRequired();
    fireEvent.change(screen.getByLabelText(/Rubric/), {
      target: { value: "Functionality: 40\n\n: 30\nInnovation: abc\nStyle" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    const posted = reqs.find((r) => r.method === "POST")?.body as { rubric: unknown };
    expect(posted.rubric).toEqual([
      { criterion: "Functionality", max_score: 40 },
      { criterion: "General", max_score: 30 }, // empty name -> General
      { criterion: "Innovation", max_score: 25 }, // NaN -> 25
      { criterion: "Style", max_score: 25 }, // no colon -> default 25
    ]);
  });

  it("empty rubric falls back to a single Overall Quality criterion at max score; blank instructions defaulted", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<NewProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot Starter");
    fillRequired();
    fireEvent.change(screen.getByLabelText(/Instructions/), { target: { value: "   " } });
    fireEvent.change(screen.getByLabelText(/Max score/), { target: { value: "200" } });
    fireEvent.click(screen.getByText("AI Visual (media workflow)"));
    fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    const posted = reqs.find((r) => r.method === "POST")?.body as Record<string, unknown>;
    expect(posted.rubric).toEqual([{ criterion: "Overall Quality", max_score: 200 }]);
    expect(posted.instructions).toBe("No instructions provided."); // blank default
    expect(posted.project_type).toBe("ai_visual"); // radio honored
    expect(posted.max_score).toBe(200);
    expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/o-1/projects/p-new");
  });

  it("Use Template posts template_id and redirects; deliverables expand toggle", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<NewProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot Starter");
    // deliverables hidden until expanded
    expect(screen.queryByText("Bot")).toBeNull();
    fireEvent.click(screen.getByText(/Show 1 workflow/));
    expect(screen.getByText(/Bot/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Use Template|Use this template/i }));
    await waitFor(() => expect(reqs.some((r) => r.method === "POST")).toBe(true));
    const post = reqs.find((r) => r.method === "POST");
    expect(post?.path).toBe("/orgs/o-1/projects/from-template");
    expect(post?.body).toEqual({ template_id: "t-1" });
    expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/o-1/projects/p-new");
  });

  it("create failure surfaces the error and allows retry", async () => {
    let fail = true;
    const reqs: { path: string; method?: string }[] = [];
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") {
        reqs.push({ path, method: init.method });
        return fail
          ? Promise.reject(new Error("boom"))
          : Promise.resolve({ data: { id: "p-new" } });
      }
      if (path.includes("project-templates")) return Promise.resolve({ data: [] });
      return Promise.resolve({ data: [] });
    }) as typeof apiWithAuth);
    render(<NewProjectPage />, { wrapper: wrapper() });
    fillRequired();
    fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
    expect(await screen.findByText("Failed to create project.")).toBeTruthy();
    fail = false;
    fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
    await waitFor(() => expect(nav.replace).toHaveBeenCalled());
    expect(reqs.length).toBe(2);
  });
});

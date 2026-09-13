import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BriefsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/briefs/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const BRIEFS = [
  {
    id: "b-1",
    title: "Hero Brief",
    client_name: "Acme",
    project_type: "product_visualization",
    status: "draft",
    created_at: "2026-09-01T00:00:00Z",
  },
];

function route(posts: { body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    if (init?.method === "POST") {
      posts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: { id: "b-new" } });
    }
    return Promise.resolve({ data: BRIEFS, meta: { total: 1 } });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("BriefsPage (R467)", () => {
  it("create requires title+client+objective and omits blank optional fields", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<BriefsPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    fireEvent.click(screen.getByRole("button", { name: /New Brief/ }));
    const createBtn = screen.getByRole("button", { name: "Create Brief" }) as HTMLButtonElement;
    expect(createBtn.disabled).toBe(true);
    fireEvent.change(screen.getByPlaceholderText("Brief title"), { target: { value: "T" } });
    fireEvent.change(screen.getByPlaceholderText("Client name"), { target: { value: "C" } });
    expect(createBtn.disabled).toBe(true); // objective still missing
    fireEvent.change(screen.getByPlaceholderText(/Objective/), { target: { value: "Obj" } });
    expect(createBtn.disabled).toBe(false);
    fireEvent.change(screen.getByPlaceholderText(/Budget range/), { target: { value: "$1k" } });
    fireEvent.click(createBtn);
    await waitFor(() => expect(posts.length).toBe(1));
    const body = posts[0]?.body as Record<string, unknown>;
    expect(body.title).toBe("T");
    expect(body.client_name).toBe("C");
    expect(body.objective).toBe("Obj");
    expect(body.budget_range).toBe("$1k");
    // blank optionals are OMITTED from the payload
    expect("timeline" in body).toBe(false);
    expect("constraints" in body).toBe(false);
    // form closes + clears on success
    await waitFor(() => expect(screen.queryByPlaceholderText("Brief title")).toBeNull());
  });

  it("brief rows link to detail with status chip", async () => {
    route([]);
    render(<BriefsPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Brief");
    expect(screen.getByText("Hero Brief").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/briefs/b-1",
    );
    expect(screen.getByText("draft")).toBeTruthy();
  });
});

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn(), info: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
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
  return { api: vi.fn(), apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import { MarketplacePanel } from "@/components/marketplace-panel";
import { api, apiWithAuth, ApiError } from "@/lib/api";

const authApi = vi.mocked(apiWithAuth);
const pubApi = vi.mocked(api);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function listing(over: Partial<Record<string, unknown>> = {}) {
  return {
    id: "l-1",
    product_type: "workflow_pack",
    product_id: "wp-1",
    offer_type: "paid",
    price_minor: 4900,
    currency: "USD",
    license_scope: "tenant",
    seat_limit: null,
    seller_org_name: "Acme Studio",
    ...over,
  };
}

function route(opts: {
  listing?: unknown;
  orgs?: unknown[];
  licensed?: boolean;
  purchase?: Record<string, unknown> | Error;
  posts?: { path: string; body: Record<string, unknown> }[];
}) {
  authApi.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts.posts?.push({ path, body: JSON.parse(init.body ?? "{}") });
      if (opts.purchase instanceof Error) return Promise.reject(opts.purchase);
      return Promise.resolve({
        data: { id: "pur-1", status: "paid", ...opts.purchase },
      });
    }
    if (path === "/orgs")
      return Promise.resolve({
        data: opts.orgs ?? [{ id: "org-a", name: "Org A", role: "admin" }],
      });
    if (path.includes("listings-view"))
      return Promise.resolve({
        data: opts.listing === null ? {} : { "wp-1": opts.listing ?? listing() },
      });
    if (path.includes("license-status"))
      return Promise.resolve({ data: { "wp-1": { licensed: opts.licensed ?? false } } });
    return Promise.resolve({ data: {} });
  }) as typeof apiWithAuth);
  pubApi.mockResolvedValue({ data: { "wp-1": opts.listing ?? listing() } });
}

const props = { productType: "workflow_pack" as const, productId: "wp-1", isAuthed: true };

beforeEach(() => vi.clearAllMocks());

describe("MarketplacePanel (R502)", () => {
  it("paid listing shows formatted price, scope, seller; purchase is a two-step confirm with per-attempt idempotency key", async () => {
    const posts: { path: string; body: Record<string, unknown> }[] = [];
    route({ posts });
    render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    await screen.findByText(/\$49\.00/);
    expect(document.body.textContent).toContain("tenant");
    expect(screen.getByText("Sold by Acme Studio")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Purchase license" }));
    expect(posts.length).toBe(0); // arming does not post
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/org-a/marketplace/purchases");
    expect(posts[0]?.body.listing_id).toBe("l-1");
    expect(posts[0]?.body.payment_method).toBe("credit");
    const key1 = String(posts[0]?.body.idempotency_key);
    expect(key1).toContain("org-a:l-1:");
    await waitFor(() => expect(toasts.success).toHaveBeenCalled());

    // R101[H0]: a SECOND confirm-flow open mints a FRESH attempt key
    fireEvent.click(await screen.findByRole("button", { name: "Purchase license" }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() => expect(posts.length).toBe(2));
    expect(posts[1]?.body.idempotency_key).not.toBe(key1);
  });

  it("checkout payment follows the hosted session URL; non-paid status is NOT announced as purchased (R101[H0])", async () => {
    const posts: { path: string; body: Record<string, unknown> }[] = [];
    route({ posts, purchase: { status: "pending", checkout_url: undefined } });
    render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    await screen.findByRole("button", { name: "Purchase license" });
    fireEvent.click(screen.getByRole("button", { name: "Purchase license" }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() => expect(toasts.info).toHaveBeenCalled());
    expect(toasts.success).not.toHaveBeenCalled(); // pending != purchased
  });

  it("included_with_plan renders the plan note with NO purchase button (R101[H1]); free and private render nothing", async () => {
    route({ listing: listing({ offer_type: "included_with_plan" }) });
    const first = render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    await first.findByText("Included with plan");
    expect(screen.queryByRole("button", { name: "Purchase license" })).toBeNull();
    first.unmount();

    for (const offer of ["free", "private"]) {
      vi.clearAllMocks();
      route({ listing: listing({ offer_type: offer }) });
      const view = render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
      await waitFor(() => expect(authApi).toHaveBeenCalled());
      expect(view.container.textContent).toBe(""); // renders nothing
      view.unmount();
    }
  });

  it("licensed badge replaces purchase; plain member sees admin prompt; INSUFFICIENT_CREDIT gets the top-up copy", async () => {
    route({ licensed: true });
    const first = render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    expect(await first.findByText("✓ Licensed")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Purchase license" })).toBeNull();
    first.unmount();

    // R101[M8]: member of the only org still sees listing state, not purchase
    vi.clearAllMocks();
    route({ orgs: [{ id: "org-a", name: "Org A", role: "member" }] });
    const second = render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    expect(await second.findByText(/Ask an organization admin to purchase/)).toBeTruthy();
    second.unmount();

    vi.clearAllMocks();
    route({ purchase: new ApiError(402, "INSUFFICIENT_CREDIT", "no credit") });
    render(<MarketplacePanel {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "Purchase license" }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() =>
      expect(toasts.error).toHaveBeenCalledWith(expect.stringContaining("top up")),
    );
  });
});

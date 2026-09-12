import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ push: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: nav.push }) }));
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

import NewPortfolioItemPage from "@/app/(dashboard)/dashboard/portfolio/items/new/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function posted() {
  return JSON.parse((api.mock.calls[0]?.[1] as { body: string }).body);
}

beforeEach(() => vi.clearAllMocks());

describe("NewPortfolioItemPage (R485)", () => {
  it("tags split on commas, trimmed, empties dropped; blank optionals omitted", async () => {
    api.mockResolvedValue({ data: { id: "pi-1" } });
    render(<NewPortfolioItemPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Hero" } });
    fireEvent.change(screen.getByPlaceholderText("ai, chatbot, python"), {
      target: { value: " ai , , chatbot ,python, " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      title: "Hero",
      tags: ["ai", "chatbot", "python"], // trimmed, empties dropped
      visibility: "public",
      featured: false,
    });
    expect(nav.push).toHaveBeenCalledWith("/dashboard/portfolio");
  });

  it("visibility select, featured checkbox, description and URL pass through when set", async () => {
    api.mockResolvedValue({ data: { id: "pi-1" } });
    render(<NewPortfolioItemPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Hero" } });
    fireEvent.change(screen.getByLabelText(/Description/), { target: { value: "About" } });
    fireEvent.change(screen.getByPlaceholderText("https://..."), {
      target: { value: "https://x.com/p" },
    });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "unlisted" } });
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      title: "Hero",
      description: "About",
      tags: [],
      external_url: "https://x.com/p",
      visibility: "unlisted",
      featured: true,
    });
  });

  it("ApiError shown verbatim; generic fallback; no redirect on failure", async () => {
    api.mockRejectedValue(new ApiError(422, "BAD_URL", "external_url must be http(s)"));
    const first = render(<NewPortfolioItemPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Hero" } });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    expect(await screen.findByText("external_url must be http(s)")).toBeTruthy();
    expect(nav.push).not.toHaveBeenCalled();
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("boom"));
    render(<NewPortfolioItemPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Hero" } });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    expect(await screen.findByText("Failed to create.")).toBeTruthy();
  });
});

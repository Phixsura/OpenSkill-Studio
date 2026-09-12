import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
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

import OrgSettingsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/settings/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ORG = { id: "o-1", name: "North School", description: "About us" };

function route(puts: { body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    if (init?.method === "PUT") {
      puts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: ORG });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("OrgSettingsPage (R465)", () => {
  it("prefills, saves the name and NULLS a cleared description", async () => {
    const puts: { body: unknown }[] = [];
    route(puts);
    render(<OrgSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("Organization Settings");
    await waitFor(() =>
      expect((screen.getByDisplayValue("North School") as HTMLInputElement).value).toBe(
        "North School",
      ),
    );
    fireEvent.change(screen.getByDisplayValue("North School"), { target: { value: "Renamed" } });
    fireEvent.change(screen.getByDisplayValue("About us"), { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: /Save/ }));
    await screen.findByText("Settings saved.");
    expect(puts[0]?.body).toEqual({ name: "Renamed", description: null }); // "" -> null
  });

  it("a blank name disables save; API failure shows its message", async () => {
    route([]);
    const r1 = render(<OrgSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("Organization Settings");
    await waitFor(() => expect(screen.getByDisplayValue("North School")).toBeTruthy());
    fireEvent.change(screen.getByDisplayValue("North School"), { target: { value: "   " } });
    expect((screen.getByRole("button", { name: /Save/ }) as HTMLButtonElement).disabled).toBe(true);
    r1.unmount();

    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "PUT")
        return Promise.reject(
          new (ApiError as new (s: number, c: string, m: string) => Error)(
            409,
            "NAME_TAKEN",
            "Name already in use",
          ),
        );
      return Promise.resolve({ data: ORG });
    }) as typeof apiWithAuth);
    render(<OrgSettingsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByDisplayValue("North School")).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: /Save/ }));
    expect(await screen.findByText("Name already in use")).toBeTruthy();
  });
});

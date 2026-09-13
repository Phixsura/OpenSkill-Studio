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

import EvalSettingsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/evaluation/settings/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SETTINGS = {
  enabled: true,
  monthly_budget_usd: 100,
  default_model: "claude-sonnet-5",
  auto_evaluate: false,
  pass_threshold: 0.6,
};

function route(puts: { body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    if (init?.method === "PUT") {
      puts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: SETTINGS });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("EvalSettingsPage (R454)", () => {
  it("prefills fields from settings and saves the full payload", async () => {
    const puts: { body: unknown }[] = [];
    route(puts);
    render(<EvalSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation Settings");
    // wait for the load->sync effect: budget prefilled to 100 and enable checked
    await waitFor(() =>
      expect(
        (screen.getByPlaceholderText("Leave empty for unlimited") as HTMLInputElement).value,
      ).toBe("100"),
    );
    expect((screen.getByLabelText("Enable AI Evaluation") as HTMLInputElement).checked).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));
    await waitFor(() => expect(puts.length).toBe(1));
    expect(puts[0]?.body).toMatchObject({
      enabled: true,
      monthly_budget_usd: 100,
      default_model: "claude-sonnet-5",
      auto_evaluate: false,
      pass_threshold: 0.6,
    });
    await screen.findByText("Settings saved.");
  });

  it("an empty budget saves monthly_budget_usd = null (unlimited), not NaN", async () => {
    const puts: { body: unknown }[] = [];
    route(puts);
    render(<EvalSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation Settings");
    fireEvent.change(screen.getByPlaceholderText("Leave empty for unlimited"), {
      target: { value: "" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));
    await waitFor(() => expect(puts.length).toBe(1));
    expect((puts[0]?.body as { monthly_budget_usd: number | null }).monthly_budget_usd).toBeNull();
  });

  it("a blank threshold OMITS pass_threshold (so it doesn't wipe the stored value)", async () => {
    const puts: { body: unknown }[] = [];
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      if (init?.method === "PUT") {
        puts.push({ body: JSON.parse(init.body ?? "{}") });
        return Promise.resolve({ data: {} });
      }
      return Promise.resolve({ data: { ...SETTINGS, pass_threshold: null } });
    }) as typeof apiWithAuth);
    render(<EvalSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation Settings");
    // the threshold field defaulted to "0.6" when null; clear it
    const inputs = screen.getAllByRole("spinbutton"); // number inputs
    const thresholdInput = inputs[inputs.length - 1] as HTMLInputElement;
    fireEvent.change(thresholdInput, { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));
    await waitFor(() => expect(puts.length).toBe(1));
    expect("pass_threshold" in (puts[0]?.body as object)).toBe(false);
  });

  it("save failure surfaces the API message; a non-ApiError shows the generic red one", async () => {
    // an ApiError message is shown verbatim
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "PUT")
        return Promise.reject(new (ApiErrorClass())(422, "BAD", "Budget too low"));
      return Promise.resolve({ data: SETTINGS });
    }) as typeof apiWithAuth);
    const r1 = render(<EvalSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation Settings");
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));
    expect(await screen.findByText("Budget too low")).toBeTruthy();
    r1.unmount();

    // a NON-ApiError falls back to the generic "Failed to save." shown in red
    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "PUT") return Promise.reject(new Error("boom"));
      return Promise.resolve({ data: SETTINGS });
    }) as typeof apiWithAuth);
    render(<EvalSettingsPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation Settings");
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));
    const msg = await screen.findByText("Failed to save.");
    expect(msg.className).toContain("text-red-600");
  });
});

import { ApiError } from "@/lib/api";
function ApiErrorClass() {
  return ApiError as new (s: number, c: string, m: string) => Error;
}

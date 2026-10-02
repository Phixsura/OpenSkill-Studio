import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/x/assignments",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useParams: () => ({ experimentId: "E".repeat(26) }),
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import AssignmentsPage from "@/app/(dashboard)/dashboard/experiments/[experimentId]/assignments/page";
import GuardrailsPage from "@/app/(dashboard)/dashboard/experiments/[experimentId]/guardrails/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function mockDiagnostics({ srm = false } = {}) {
  api.mockImplementation(async (path: string) => {
    const p = String(path);
    if (p.endsWith("/assignments")) {
      return { data: { variants: { control: 120, treatment: 80 }, holdout: 5, total: 205 } };
    }
    if (p.endsWith("/exposures/stats")) {
      return {
        data: {
          funnel: {
            control: { assigned: 120, exposed_units: 60 },
            treatment: { assigned: 80, exposed_units: 70 },
          },
          holdout: 5,
          last_exposure_at: "2026-10-01T12:00:00Z",
        },
      };
    }
    if (p.includes("/guardrails/events")) {
      return {
        data: srm
          ? [
              {
                id: "G".repeat(26),
                guardrail_key: "__srm__",
                action: "alerted",
                auto: true,
                detail: { chi2: 122.5, df: 1 },
                created_at: "2026-10-01T00:00:00Z",
              },
            ]
          : [],
      };
    }
    if (p.includes(":preview")) {
      return {
        data: {
          eligible: true,
          variant_key: "treatment",
          bucket: 1234,
          is_holdout: false,
        },
      };
    }
    return { data: [] };
  });
}

beforeEach(() => vi.clearAllMocks());

describe("Assignment diagnostics (ADR-017 Part L)", () => {
  it("shows the funnel numbers and the SRM banner when an __srm__ event exists", async () => {
    mockDiagnostics({ srm: true });
    render(<AssignmentsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/Sample-ratio mismatch detected/)).toBeTruthy();
    expect(screen.getByText("120")).toBeTruthy(); // control assigned
    expect(screen.getByText("70")).toBeTruthy(); // treatment exposed units
  });

  it("no SRM banner without an __srm__ event; preview posts and renders", async () => {
    mockDiagnostics({ srm: false });
    render(<AssignmentsPage />, { wrapper: wrapper() });
    await screen.findByText("120");
    expect(screen.queryByText(/Sample-ratio mismatch detected/)).toBeNull();
    const unitInput = screen.getByLabelText(/Unit id/);
    fireEvent.change(unitInput, { target: { value: "u-123" } });
    fireEvent.click(screen.getByRole("button", { name: /Preview/ }));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).includes(":preview"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).includes(":preview"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.unit_id).toBe("u-123");
    await waitFor(() => expect(screen.getAllByText(/treatment/).length).toBeGreaterThanOrEqual(2)); // table row + preview result both show it
  });
});

describe("Guardrail dashboard", () => {
  it("shows the last-exposure data-flow line", async () => {
    mockDiagnostics({ srm: false });
    render(<AssignmentsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/Last exposure:/)).toBeTruthy();
    await waitFor(() => expect(screen.queryByText(/none recorded/)).toBeNull());
  });

  it("renders guardrail events with key and action", async () => {
    mockDiagnostics({ srm: true });
    render(<GuardrailsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/__srm__/)).toBeTruthy();
    expect(screen.getByText(/alerted/)).toBeTruthy();
  });
});

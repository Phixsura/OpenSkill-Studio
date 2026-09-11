import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ partnerId: "pt-1", statementId: "st-1" }),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
const refreshMock = vi.hoisted(() => vi.fn());
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  sharedRefresh: refreshMock,
  ApiError: class extends Error {
    constructor(
      public status: number,
      public code: string,
      msg: string,
    ) {
      super(msg);
    }
  },
}));
const tokenState = vi.hoisted(() => ({ accessToken: "tok-old" as string | null }));
vi.mock("@/stores/auth", () => ({
  useAuthStore: { getState: () => ({ accessToken: tokenState.accessToken }) },
}));

import StatementDetailPage from "@/app/(dashboard)/partner/[partnerId]/statements/[statementId]/page";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const STMT = {
  id: "st-1",
  period: "2026-08",
  status: "finalized",
  currency: "EUR",
  opening_adjustments_minor: 100,
  gross_revenue_minor: 500000,
  refunds_minor: 2500,
  share_total_minor: 100000,
  manual_adjustments_minor: -300,
  net_amount_minor: 99800,
  finalized_at: "2026-09-01T00:00:00Z",
  external_payment_ref: "SEPA-778",
  entry_count: 4,
  entries: [
    {
      id: "e-null",
      source_type: "invoice",
      source_id: "src-aaaaaaaaaaaaaa",
      revenue_base_minor: null,
      rule_snapshot: { rule_type: "percentage_of_margin" },
      share_amount_minor: 1200,
      currency: "EUR",
      status: "accrued",
      created_at: "2026-08-02T00:00:00Z",
    },
    {
      id: "e-margin0",
      source_type: "invoice",
      source_id: "src-bbbbbbbbbbbbbb",
      revenue_base_minor: 0,
      rule_snapshot: { rule_type: "percentage_of_margin" },
      share_amount_minor: 340,
      currency: "EUR",
      status: "accrued",
      created_at: "2026-08-03T00:00:00Z",
    },
    {
      id: "e-zero",
      source_type: "credit",
      source_id: "src-cccccccccccccc",
      revenue_base_minor: 0,
      rule_snapshot: { rule_type: "percentage_of_revenue" },
      share_amount_minor: 0,
      currency: "EUR",
      status: "accrued",
      created_at: "2026-08-04T00:00:00Z",
    },
    {
      id: "e-real",
      source_type: "invoice",
      source_id: "src-dddddddddddddd",
      revenue_base_minor: 25000,
      rule_snapshot: { rule_type: "percentage_of_revenue" },
      share_amount_minor: 5000,
      currency: "EUR",
      status: "accrued",
      created_at: "2026-08-05T00:00:00Z",
    },
  ],
};

beforeEach(() => {
  api.mockReset();
  refreshMock.mockReset();
  toasts.error.mockReset();
  tokenState.accessToken = "tok-old";
  api.mockResolvedValue({ data: STMT });
  vi.stubGlobal(
    "URL",
    Object.assign(URL, { createObjectURL: vi.fn(() => "blob:x"), revokeObjectURL: vi.fn() }),
  );
});

describe("StatementDetailPage (R406)", () => {
  it("renders the six money tiles in the STATEMENT currency incl. negative manual adj.", async () => {
    render(<StatementDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Statement 2026-08")).toBeTruthy();
    const body = document.body.textContent ?? "";
    for (const v of [500000, 2500, 100000, 100, 99800]) {
      expect(body).toContain(formatMinor(v, "EUR"));
    }
    expect(body).toContain(formatMinor(-300, "EUR"));
    expect(body).toContain("Finalized");
    expect(body).toContain("Paid ref SEPA-778");
    expect(body).toContain("Entries (4)");
  });

  it("masks the revenue base for margin-rule entries (null AND zero) but shows real zero for revenue rules", async () => {
    render(<StatementDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Statement 2026-08");
    const rows = Array.from(document.querySelectorAll("tbody tr"));
    const baseOf = (frag: string) =>
      rows.find((r) => r.textContent?.includes(frag))?.children[2]?.textContent;
    expect(baseOf("src-aaaaaaaa")).toBe("—"); // null base
    expect(baseOf("src-bbbbbbbb")).toBe("—"); // 0 + percentage_of_margin
    expect(baseOf("src-cccccccc")).toBe(formatMinor(0, "EUR")); // genuine zero
    expect(baseOf("src-dddddddd")).toBe(formatMinor(25000, "EUR"));
  });

  it("CSV export reads the token at CLICK time and sends it as a Bearer header", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      blob: () => Promise.resolve(new Blob(["csv"])),
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<StatementDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Statement 2026-08");
    tokenState.accessToken = "tok-rotated"; // rotate AFTER render, BEFORE click
    fireEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    const [url, init] = fetchMock.mock.calls[0] as [
      string,
      RequestInit & { headers: Record<string, string> },
    ];
    expect(String(url)).toContain("/partners/pt-1/statements/st-1/export.csv");
    expect(init.headers.Authorization).toBe("Bearer tok-rotated");
  });

  it("on 401 the export refreshes ONCE and retries with the new token", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 401 })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(new Blob(["csv"])),
      });
    vi.stubGlobal("fetch", fetchMock);
    refreshMock.mockResolvedValue("tok-fresh");
    render(<StatementDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Statement 2026-08");
    fireEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    const retryInit = fetchMock.mock.calls[1]?.[1] as { headers: Record<string, string> };
    expect(retryInit.headers.Authorization).toBe("Bearer tok-fresh");
    expect(toasts.error).not.toHaveBeenCalled();
  });

  it("refresh failure on export → session-expired toast, no crash", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401 }));
    refreshMock.mockRejectedValue(new Error("nope"));
    render(<StatementDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Statement 2026-08");
    fireEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() =>
      expect(toasts.error).toHaveBeenCalledWith("Session expired — please log in again"),
    );
  });

  it("non-401 export failure → generic failure toast", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    render(<StatementDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Statement 2026-08");
    fireEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("CSV export failed"));
  });
});

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ApplicationsPage from "@/app/(dashboard)/dashboard/applications/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("ApplicationsPage detail drawer (R584)", () => {
  it("loads timeline and messages from their OWN endpoints, not the detail payload", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/talent/applications?")) {
        return Promise.resolve({
          data: [
            {
              id: "APP1",
              opportunity_id: "OPP1",
              user_id: "U1",
              status: "submitted",
              cover_note: null,
              created_at: "2026-10-01T00:00:00Z",
              updated_at: "2026-10-01T00:00:00Z",
            },
          ],
          meta: { next_cursor: null, has_more: false },
        });
      }
      if (path === "/talent/applications/APP1") {
        return Promise.resolve({ data: { evidence_bundle: { portfolio: "x" } } });
      }
      if (path === "/talent/applications/APP1/timeline") {
        return Promise.resolve({
          data: [{ stage: "submitted", timestamp: "2026-10-01T00:00:00Z", actor: "U1" }],
        });
      }
      if (path === "/talent/applications/APP1/messages") {
        return Promise.resolve({
          data: [
            { id: "M1", content: "Thanks for applying", sender_role: "employer", read_at: null },
          ],
        });
      }
      if (path.startsWith("/talent/opportunities/")) {
        return Promise.resolve({
          data: {
            id: "OPP1",
            title: "AI Designer",
            opportunity_type: "job",
            employer_org_id: "O1",
            location_mode: "remote",
            status: "open",
          },
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<ApplicationsPage />, { wrapper: wrapper() });
    // the card renders once applications load
    await waitFor(() => expect(screen.getByText("▼ Show details")).toBeTruthy());
    fireEvent.click(screen.getByText("▼ Show details"));

    // timeline (stage field) and messages (content) must appear
    await waitFor(() => expect(screen.getByText("submitted")).toBeTruthy());
    expect(screen.getByText("Thanks for applying")).toBeTruthy();
    expect(screen.getByText(/Messages \(1\)/)).toBeTruthy();
  });
});

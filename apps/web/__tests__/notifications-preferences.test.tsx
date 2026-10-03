import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import NotificationsPage from "@/app/(dashboard)/dashboard/notifications/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("Notification preferences (round 139)", () => {
  it("lists every experiment toggle incl. the weekly digest and PUTs on change", async () => {
    mockApi.mockImplementation(async (path: string, init?: { method?: string }) => {
      if (init?.method === "PUT") return { data: [] };
      if (String(path).includes("unread-count")) return { data: { unread_count: 0 } };
      return { data: [] };
    });
    render(<NotificationsPage />, { wrapper: createWrapper() });
    fireEvent.click(screen.getByText(/settings/i));
    expect(await screen.findByText("Experiment Weekly Digest")).toBeTruthy();
    expect(screen.getByText("Experiment Guardrails & Alerts")).toBeTruthy();
    expect(screen.getByText(/Experiment Significance/)).toBeTruthy();

    const digestRow = screen.getByText("Experiment Weekly Digest").closest("label");
    const checkbox = digestRow?.querySelector("input[type=checkbox]");
    expect(checkbox).toBeTruthy();
    fireEvent.click(checkbox as HTMLInputElement);
    await waitFor(() => {
      const call = mockApi.mock.calls.find((c) => c[1]?.method === "PUT");
      expect(call).toBeTruthy();
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body.preferences).toEqual([{ event_type: "experiment_digest", enabled: false }]);
    });
  });
});

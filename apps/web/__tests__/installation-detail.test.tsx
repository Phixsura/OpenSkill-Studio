import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1", installId: "inst-1" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import InstallationDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/installations/[installId]/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

const INSTALL = {
  id: "inst-1",
  org_id: "org-1",
  pack_id: "pack-1",
  release_id: "rel-1",
  installed_version: "1.0.0",
  status: "active",
  installed_by: "user-1",
  installed_at: "2026-05-01T12:00:00Z",
  update_available: false,
  latest_version: undefined,
};

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("InstallationDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("shows error state on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load installation/),
    ).toBeDefined();
  });

  it("renders installation details", async () => {
    mockApiWithAuth.mockResolvedValue({ data: INSTALL });
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Installation Detail")).toBeDefined();
    expect(screen.getByText("v1.0.0")).toBeDefined();
    expect(screen.getByText("active")).toBeDefined();
    expect(screen.getByText("Pack ID")).toBeDefined();
    expect(screen.getByText("pack-1")).toBeDefined();
  });

  it("renders Fork and Remove buttons", async () => {
    mockApiWithAuth.mockResolvedValue({ data: INSTALL });
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Fork")).toBeDefined();
    expect(screen.getByText("Remove")).toBeDefined();
  });

  it("shows update available banner when applicable", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: { ...INSTALL, update_available: true, latest_version: "2.0.0" },
    });
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Update available: v2.0.0/),
    ).toBeDefined();
    expect(screen.getByText("View Changes")).toBeDefined();
  });

  it("calls diff API when View Changes is clicked", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: { ...INSTALL, update_available: true, latest_version: "2.0.0" },
    });
    render(<InstallationDetailPage />, { wrapper: createWrapper() });

    const viewChangesBtn = await screen.findByText("View Changes");

    mockApiWithAuth.mockResolvedValueOnce({
      data: {
        added: [{ type: "skill", logical_id: "s1", name: "New Skill" }],
        changed: [],
        removed: [],
        conflicts: [],
      },
    });

    fireEvent.click(viewChangesBtn);

    await waitFor(() => {
      expect(mockApiWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/diff"),
      );
    });
  });

  it("renders details section with metadata", async () => {
    mockApiWithAuth.mockResolvedValue({ data: INSTALL });
    render(<InstallationDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Details")).toBeDefined();
    expect(screen.getByText("Release ID")).toBeDefined();
    expect(screen.getByText("Installed by")).toBeDefined();
    expect(screen.getByText("user-1")).toBeDefined();
  });
});

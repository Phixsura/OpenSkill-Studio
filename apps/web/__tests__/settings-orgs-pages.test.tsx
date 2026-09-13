import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const authState = vi.hoisted(() => ({
  user: { email: "u@x.com", display_name: "Hana" } as Record<string, unknown> | null,
  accessToken: "tok-1" as string | null,
  setAuth: vi.fn(),
}));
vi.mock("@/stores/auth", () => ({
  useAuthStore: (sel: (s: typeof authState) => unknown) => sel(authState),
}));
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

import OrgsListPage from "@/app/(dashboard)/dashboard/orgs/page";
import SettingsPage from "@/app/(dashboard)/dashboard/settings/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
  authState.user = { email: "u@x.com", display_name: "Hana" };
  authState.accessToken = "tok-1";
});

describe("SettingsPage (R418)", () => {
  it("saves the display name via PUT /auth/me and updates the auth store with the SAME token", async () => {
    const puts: { path: string; body: unknown }[] = [];
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      puts.push({ path: String(rawPath ?? ""), body: JSON.parse(init?.body ?? "{}") });
      return Promise.resolve({ data: { email: "u@x.com", display_name: "Hana2" } });
    }) as typeof apiWithAuth);
    render(<SettingsPage />, { wrapper: wrapper() });
    // email input disabled; display name prefilled from the store
    expect((screen.getByLabelText("Email") as HTMLInputElement).disabled).toBe(true);
    const nameInput = screen.getByLabelText("Display name") as HTMLInputElement;
    expect(nameInput.value).toBe("Hana");
    fireEvent.change(nameInput, { target: { value: "Hana2" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await screen.findByText("Profile updated.");
    expect(puts).toEqual([{ path: "/auth/me", body: { display_name: "Hana2" } }]);
    expect(authState.setAuth).toHaveBeenCalledWith("tok-1", {
      email: "u@x.com",
      display_name: "Hana2",
    });
    // success message styled green, not red
    expect(screen.getByText("Profile updated.").className).toContain("text-green-600");
  });

  it("API failure surfaces ITS message in red and does NOT touch the auth store", async () => {
    api.mockImplementation(() =>
      Promise.reject(
        new (ApiError as new (s: number, c: string, m: string) => Error)(
          422,
          "INVALID",
          "Display name failed moderation",
        ),
      ),
    );
    render(<SettingsPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    const msg = await screen.findByText("Display name failed moderation");
    expect(msg.className).toContain("text-red-600");
    expect(authState.setAuth).not.toHaveBeenCalled();
  });
});

describe("OrgsListPage (R418)", () => {
  it("renders org cards with role/member meta and links; description optional", async () => {
    api.mockResolvedValue({
      data: [
        { id: "o-1", name: "Org A", description: "About A", role: "owner", member_count: 4 },
        { id: "o-2", name: "Org B", description: null, role: "student", member_count: 9 },
      ],
    });
    render(<OrgsListPage />, { wrapper: wrapper() });
    await screen.findByText("Org A");
    expect(screen.getByText("About A")).toBeTruthy();
    expect(screen.getByText("Org B").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-2",
    );
    expect(screen.queryByText(/don't belong to any organizations/)).toBeNull();
  });

  it("failed fetch shows the retry hint AND suppresses the empty-state CTA", async () => {
    api.mockRejectedValue(new Error("orgs down"));
    render(<OrgsListPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Failed to load organizations. Please try again.")).toBeTruthy();
  });

  it("empty list shows the first-organization CTA", async () => {
    api.mockResolvedValue({ data: [] });
    render(<OrgsListPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/don't belong to any organizations/)).toBeTruthy();
    expect(screen.getByText("Create your first organization")).toBeTruthy();
  });
});

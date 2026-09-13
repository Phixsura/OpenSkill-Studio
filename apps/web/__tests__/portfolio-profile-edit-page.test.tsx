import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import EditProfilePage from "@/app/(dashboard)/dashboard/portfolio/profile/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PROFILE = {
  username: "ada",
  headline: "AI artist",
  bio: null,
  location: "London",
  website_url: null,
};

function route(reqs?: { path: string; method?: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method) {
      reqs?.push({
        path,
        method: init.method,
        body: init.body ? JSON.parse(init.body) : undefined,
      });
      return Promise.resolve({ data: { ok: true } });
    }
    return Promise.resolve({ data: PROFILE });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("EditProfilePage (R486)", () => {
  it("save converts empty strings to null (clearing a field really clears it)", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<EditProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Edit Profile");
    // clear headline, set bio
    fireEvent.change(screen.getByLabelText("Headline"), { target: { value: "" } });
    fireEvent.change(screen.getByLabelText("Bio"), { target: { value: "New bio" } });
    fireEvent.click(screen.getByRole("button", { name: "Save Changes" }));
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.method).toBe("PUT");
    expect(reqs[0]?.path).toBe("/portfolio/profile");
    expect(reqs[0]?.body).toEqual({
      headline: null, // cleared -> null, not ""
      bio: "New bio",
      location: "London",
      website_url: null,
    });
    expect(await screen.findByText("Profile saved.")).toBeTruthy();
  });

  it("username Change is disabled until the draft differs and is non-blank; PUT sends the trimmed draft", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<EditProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Edit Profile");
    const changeBtn = screen.getByRole("button", { name: "Change" }) as HTMLButtonElement;
    expect(changeBtn.disabled).toBe(true); // no draft yet
    const input = screen.getByLabelText("Username");
    fireEvent.change(input, { target: { value: " ada " } }); // trims to current -> still disabled
    expect(changeBtn.disabled).toBe(true);
    fireEvent.change(input, { target: { value: "  " } }); // blank -> disabled
    expect(changeBtn.disabled).toBe(true);
    fireEvent.change(input, { target: { value: " ada2 " } });
    expect(changeBtn.disabled).toBe(false);
    // live URL preview reflects the trimmed draft
    expect(document.body.textContent).toContain("/u/ada2");
    fireEvent.click(changeBtn);
    await waitFor(() => expect(reqs.length).toBe(1));
    expect(reqs[0]?.path).toBe("/portfolio/username");
    expect(reqs[0]?.body).toEqual({ username: "ada2" }); // trimmed
    expect(await screen.findByText("Username updated.")).toBeTruthy();
  });

  it("failure messages render red; load failure shows the error line", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method) return Promise.reject(new Error("username taken"));
      return Promise.resolve({ data: PROFILE });
    }) as typeof apiWithAuth);
    const first = render(<EditProfilePage />, { wrapper: wrapper() });
    await first.findByText("Edit Profile");
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "taken" } });
    fireEvent.click(screen.getByRole("button", { name: "Change" }));
    const msg = await screen.findByText("username taken");
    expect(msg.className).not.toContain("text-green-600");
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<EditProfilePage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load profile"));
  });
});

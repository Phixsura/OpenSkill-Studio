import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", profileId: "prof-1" }) }));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import RequirementProfilePage from "@/app/(dashboard)/dashboard/orgs/[orgId]/requirements/[profileId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function profile(status = "draft") {
  return {
    id: "prof-1",
    context_type: "learning",
    status,
    structured_requirements: {
      goal: "Learn compositing",
      time_budget: 120,
      required_capabilities: ["image_generation", "upscale"],
    },
    extraction_meta: {
      provenance: { goal: "extracted", time_budget: "user_entered" },
      unmatched_mentions: ["hologram", "made_up_cap"],
    },
  };
}

function route(p: Record<string, unknown>, patches: { body: unknown }[], posts: string[] = []) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "PATCH") {
      patches.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    if (init?.method === "POST") {
      posts.push(path);
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: p });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("RequirementProfilePage (R457)", () => {
  it("provenance badges: extracted vs user-entered per field; unmatched mentions listed", async () => {
    route(profile(), []);
    render(<RequirementProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Goal");
    const body = document.body.textContent ?? "";
    expect(body).toContain("AI extracted"); // goal is extracted
    expect(body).toContain("You entered"); // time_budget is user-entered
    expect(body).toContain("hologram, made_up_cap"); // unmatched mentions surfaced
    // list fields are joined for editing
    expect((screen.getByLabelText("Required capabilities") as HTMLInputElement).value).toBe(
      "image_generation, upscale",
    );
  });

  it("save PATCHes ONLY changed fields, splitting lists and nulling cleared ones", async () => {
    const patches: { body: unknown }[] = [];
    route(profile(), patches);
    render(<RequirementProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Goal");
    await waitFor(() =>
      expect((screen.getByLabelText("Goal") as HTMLInputElement).value).toBe("Learn compositing"),
    );
    // change goal, clear time_budget, edit the capabilities list
    fireEvent.change(screen.getByLabelText("Goal"), { target: { value: "New goal" } });
    fireEvent.change(screen.getByLabelText("Time budget (minutes)"), { target: { value: "" } });
    fireEvent.change(screen.getByLabelText("Required capabilities"), {
      target: { value: "upscale,  hd , " },
    });
    fireEvent.click(screen.getByRole("button", { name: /Save/ }));
    await waitFor(() => expect(patches.length).toBe(1));
    expect(patches[0]?.body).toEqual({
      edits: {
        goal: "New goal",
        time_budget: null, // cleared -> null
        required_capabilities: ["upscale", "hd"], // split + trimmed + de-blanked
      },
    });
    // scenario/output_type/etc. unchanged -> NOT sent
  });

  it("confirm POSTs and a confirmed profile disables editing", async () => {
    const posts: string[] = [];
    route(profile(), [], posts);
    const r1 = render(<RequirementProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Goal");
    fireEvent.click(screen.getByRole("button", { name: "Confirm Profile" }));
    await waitFor(() => expect(posts).toContain("/orgs/o-1/requirement-profiles/prof-1/confirm"));
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Profile confirmed"));
    r1.unmount();

    vi.clearAllMocks();
    route(profile("confirmed"), []);
    render(<RequirementProfilePage />, { wrapper: wrapper() });
    await screen.findByText("Goal");
    expect((screen.getByLabelText("Goal") as HTMLInputElement).disabled).toBe(true);
    expect(screen.queryByRole("button", { name: "Confirm Profile" })).toBeNull();
  });
});

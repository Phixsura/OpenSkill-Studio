import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ push: vi.fn() }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", projectId: "p-1" }),
  useRouter: () => ({ push: nav.push }),
}));
vi.mock("@/components/media-preview", () => ({ MediaPreview: () => <div /> }));
vi.mock("@/components/generation-data", () => ({
  GenerationData: () => <div />,
}));
const shared = vi.hoisted(() => ({ refresh: vi.fn() }));
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
  return {
    apiWithAuth: vi.fn(),
    ApiError: MockApiError,
    sharedRefresh: (...a: unknown[]) => shared.refresh(...a),
  };
});
vi.mock("@/stores/auth", () => ({
  useAuthStore: { getState: () => ({ accessToken: "stale-token" }) },
}));

import SubmitPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/[projectId]/submit/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);
const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function deliverable(over: Partial<Record<string, unknown>> = {}) {
  return {
    id: "d-file",
    name: "Hero Image",
    description: null,
    type: "file",
    required: true,
    config: { accepted_formats: ["image/png"], max_file_size_mb: 1 },
    sort_order: 1,
    ...over,
  };
}

function project(deliverables: unknown[], type = "general") {
  return { title: "Chatbot", project_type: type, deliverables };
}

function route(proj: unknown, reqs?: { path: string; method?: string; body?: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method) {
      reqs?.push({
        path,
        method: init.method,
        body: init.body ? JSON.parse(init.body) : undefined,
      });
      if (path.endsWith("/submissions")) return Promise.resolve({ data: { id: "sub-1" } });
      return Promise.resolve({ data: { ok: true } });
    }
    return Promise.resolve({ data: proj });
  }) as typeof apiWithAuth);
}

async function startDraft() {
  fireEvent.click(await screen.findByRole("button", { name: "Start Draft" }));
  await screen.findByRole("button", { name: "Submit" });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("SubmitPage (R491)", () => {
  it("pre-draft preview lists numbered deliverables with required/optional chips; Start Draft POSTs", async () => {
    const reqs: { path: string; method?: string }[] = [];
    route(
      project([
        deliverable(),
        deliverable({
          id: "d-txt",
          name: "Writeup",
          type: "markdown",
          required: false,
          sort_order: 2,
        }),
      ]),
      reqs,
    );
    render(<SubmitPage />, { wrapper: wrapper() });
    await screen.findByText("What you'll submit");
    expect(document.body.textContent).toContain("2 deliverables · 1 required");
    expect(screen.getByText("Required")).toBeTruthy();
    expect(screen.getByText("Optional")).toBeTruthy();
    await startDraft();
    expect(reqs.find((r) => r.method === "POST")?.path).toBe("/orgs/o-1/projects/p-1/submissions");
  });

  it("client pre-checks reject oversized files and wrong formats WITHOUT hitting the network", async () => {
    route(project([deliverable()]));
    render(<SubmitPage />, { wrapper: wrapper() });
    await startDraft();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    // oversize: 2MB > 1MB limit
    const big = new File([new ArrayBuffer(2 * 1024 * 1024)], "big.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [big] } });
    expect(await screen.findByText(/exceeds the 1MB limit for Hero Image/)).toBeTruthy();
    // wrong mime
    const wrong = new File(["x"], "doc.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [wrong] } });
    expect(await screen.findByText(/"application\/pdf" is not accepted/)).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("R184: upload retries once through sharedRefresh on a 401", async () => {
    route(project([deliverable()]));
    shared.refresh.mockResolvedValue("fresh-token");
    fetchMock
      .mockResolvedValueOnce({ status: 401, ok: false, json: () => Promise.resolve({}) })
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
        json: () =>
          Promise.resolve({
            data: {
              id: "f-1",
              file_name: "ok.png",
              mime_type: "image/png",
              version: 1,
              content: null,
            },
          }),
      });
    render(<SubmitPage />, { wrapper: wrapper() });
    await startDraft();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const ok = new File(["x"], "ok.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [ok] } });
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(shared.refresh).toHaveBeenCalledTimes(1);
    // the retry carried the refreshed token
    const retryHeaders = (fetchMock.mock.calls[1]?.[1] as RequestInit).headers as Record<
      string,
      string
    >;
    expect(retryHeaders.Authorization).toBe("Bearer fresh-token");
    expect(await screen.findByText("ok.png")).toBeTruthy(); // upload landed
  });

  it("prompt save validates JSON parameters + numeric seed, omits blank optionals, guards double-click", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(
      project(
        [deliverable({ id: "d-p", name: "Gen Prompt", type: "prompt", config: {} })],
        "ai_visual",
      ),
      reqs,
    );
    render(<SubmitPage />, { wrapper: wrapper() });
    await startDraft();
    fireEvent.change(screen.getByPlaceholderText("Your generation prompt..."), {
      target: { value: "  a hero shot  " },
    });
    // invalid JSON parameters blocked client-side
    const params = screen.getByPlaceholderText(/Extra parameters JSON/);
    fireEvent.change(params, { target: { value: "{not json" } });
    fireEvent.click(screen.getByRole("button", { name: /Save prompt/i }));
    expect(await screen.findByText(/Parameters must be valid JSON/)).toBeTruthy();
    expect(reqs.filter((r) => r.path.includes("prompt-items")).length).toBe(0);
    // NaN seed also blocked
    fireEvent.change(params, { target: { value: "" } });
    fireEvent.change(screen.getByPlaceholderText("Seed"), { target: { value: "abc" } });
    fireEvent.click(screen.getByRole("button", { name: /Save prompt/i }));
    expect(await screen.findByText("Seed must be a number.")).toBeTruthy();
    expect(reqs.filter((r) => r.path.includes("prompt-items")).length).toBe(0);
    fireEvent.change(screen.getByPlaceholderText("Seed"), { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: /Save prompt/i }));
    await waitFor(() => expect(reqs.filter((r) => r.path.includes("prompt-items")).length).toBe(1));
    const body = reqs.find((r) => r.path.includes("prompt-items"))?.body as Record<string, unknown>;
    expect(body.prompt).toBe("a hero shot"); // trimmed
    expect(body.deliverable_id).toBe("d-p");
    expect("negative_prompt" in body ? body.negative_prompt : undefined).toBeUndefined();
    expect("seed" in body ? body.seed : undefined).toBeUndefined();
  });

  it("Submit PUTs trimmed text items with markdown type preserved, then posts submit and redirects", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(
      project([
        deliverable({ id: "d-md", name: "Writeup", type: "markdown", config: {} }),
        deliverable({
          id: "d-link",
          name: "Demo",
          type: "link",
          required: false,
          config: {},
          sort_order: 2,
        }),
      ]),
      reqs,
    );
    render(<SubmitPage />, { wrapper: wrapper() });
    await startDraft();
    const textareas = document.querySelectorAll("textarea");
    fireEvent.change(textareas[0] as HTMLTextAreaElement, {
      target: { value: "  # My writeup  " },
    });
    fireEvent.change(screen.getByPlaceholderText("https://..."), {
      target: { value: "https://demo.example" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "PUT")).toBe(true));
    const put = reqs.find((r) => r.method === "PUT");
    expect(put?.path).toBe("/orgs/o-1/projects/p-1/submissions/sub-1");
    const items = (
      put?.body as { items: { deliverable_id: string; content: string; type: string }[] }
    ).items;
    expect(items).toContainEqual({
      deliverable_id: "d-md",
      content: "# My writeup",
      type: "markdown",
    });
    expect(items).toContainEqual({
      deliverable_id: "d-link",
      content: "https://demo.example",
      type: "text",
    });
    await waitFor(() =>
      expect(reqs.some((r) => r.path.endsWith("/submissions/sub-1/submit"))).toBe(true),
    );
    await waitFor(() => expect(nav.push).toHaveBeenCalledWith("/dashboard/orgs/o-1/projects/p-1"));
  });
});

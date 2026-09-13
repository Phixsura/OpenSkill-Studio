import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

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

import { CommentPanel } from "@/components/comment-panel";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function comment(
  over: Partial<import("@/components/annotated-media").ItemComment> = {},
): import("@/components/annotated-media").ItemComment {
  return {
    id: "c-1",
    item_id: "it-1",
    parent_id: null,
    author_id: "u-1",
    text: "root comment",
    anchor_type: "global",
    region: null,
    timestamp_ms: null,
    duration_ms: null,
    author_name: "Ada",
    created_at: "2026-09-01T00:00:00Z",
    completed: false,
    ...over,
  } as import("@/components/annotated-media").ItemComment;
}

const base = {
  orgId: "o-1",
  submissionId: "sub-1",
  itemId: "it-1",
  onChanged: vi.fn(),
  canComment: true,
};

function posted(i = 0) {
  const call = api.mock.calls[i];
  return JSON.parse((call?.[1] as { body: string }).body);
}

beforeEach(() => vi.clearAllMocks());

describe("CommentPanel (R504)", () => {
  it("global comment posts trimmed text; Enter double-submit is gated in the FUNCTION (R183)", async () => {
    let resolve!: (v: unknown) => void;
    api.mockImplementation(
      (() => new Promise((r) => (resolve = r))) as unknown as typeof apiWithAuth,
    );
    render(<CommentPanel {...base} comments={[]} />);
    const input = screen.getByPlaceholderText("Add a comment…");
    fireEvent.change(input, { target: { value: "  hello  " } });
    fireEvent.keyDown(input, { key: "Enter" });
    fireEvent.keyDown(input, { key: "Enter" }); // second Enter mid-flight
    fireEvent.keyDown(input, { key: "Enter" });
    resolve({ data: { id: "c-new" } });
    await waitFor(() => expect(base.onChanged).toHaveBeenCalled());
    expect(api).toHaveBeenCalledTimes(1); // gated in submit(), not just the button
    expect(posted()).toEqual({ item_id: "it-1", text: "hello" }); // trimmed, no anchor keys
  });

  it("pending region attaches anchor_type=region and clears after post", async () => {
    api.mockResolvedValue({ data: { id: "c-new" } });
    const onClear = vi.fn();
    render(
      <CommentPanel
        {...base}
        comments={[]}
        pendingRegion={{
          type: "rectangle" as const,
          bounds: { minX: 0.1, minY: 0.2, maxX: 0.4, maxY: 0.6 },
        }}
        onClearPendingRegion={onClear}
      />,
    );
    expect(screen.getByText(/Region selected/)).toBeTruthy();
    fireEvent.change(screen.getByPlaceholderText("Add a comment…"), {
      target: { value: "fix this area" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Post" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      item_id: "it-1",
      text: "fix this area",
      anchor_type: "region",
      region: { type: "rectangle", bounds: { minX: 0.1, minY: 0.2, maxX: 0.4, maxY: 0.6 } },
    });
    expect(onClear).toHaveBeenCalled();
  });

  it("time anchoring: checkbox anchors at the playback position; replies NEVER carry anchors", async () => {
    api.mockResolvedValue({ data: { id: "c-new" } });
    const first = render(<CommentPanel {...base} comments={[]} currentTimeMs={83500} />);
    fireEvent.click(screen.getByRole("checkbox")); // "Anchor at 1:23"
    expect(screen.getByText(/Anchor at 1:23/)).toBeTruthy();
    fireEvent.change(screen.getByPlaceholderText("Add a comment…"), {
      target: { value: "audio pops here" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Post" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      item_id: "it-1",
      text: "audio pops here",
      anchor_type: "time",
      timestamp_ms: 83500,
    });
    first.unmount();

    // reply path: parent_id wins over any pending region/time anchor
    vi.clearAllMocks();
    api.mockResolvedValue({ data: { id: "c-new" } });
    render(
      <CommentPanel
        {...base}
        comments={[comment()]}
        pendingRegion={{
          type: "rectangle" as const,
          bounds: { minX: 0.1, minY: 0.2, maxX: 0.4, maxY: 0.6 },
        }}
        currentTimeMs={1000}
      />,
    );
    fireEvent.click(screen.getByText("Reply"));
    fireEvent.change(screen.getByPlaceholderText("Write a reply…"), {
      target: { value: "agreed" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Post" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({ item_id: "it-1", text: "agreed", parent_id: "c-1" });
  });

  it("threading: replies nest under roots; region pins numbered in region order; other items filtered out", () => {
    render(
      <CommentPanel
        {...base}
        comments={[
          comment({
            id: "c-r1",
            anchor_type: "region",
            region: { type: "rectangle", bounds: { minX: 0, minY: 0, maxX: 1, maxY: 1 } },
            text: "first region",
          }),
          comment({
            id: "c-r2",
            anchor_type: "region",
            region: { type: "rectangle", bounds: { minX: 0, minY: 0, maxX: 1, maxY: 1 } },
            text: "second region",
          }),
          comment({ id: "c-reply", parent_id: "c-r1", text: "a reply" }),
          comment({ id: "c-foreign", item_id: "it-OTHER", text: "foreign comment" }),
        ]}
      />,
    );
    expect(screen.getByText("1")).toBeTruthy(); // pin index for first region
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("a reply")).toBeTruthy();
    expect(screen.queryByText("foreign comment")).toBeNull(); // item-scoped
    // time chip renders mm:ss
    expect(screen.getAllByText("Reply").length).toBe(2); // roots only, not the reply
  });

  it("canComment=false renders read-only: no composer, no Reply/Mark complete", () => {
    render(<CommentPanel {...base} canComment={false} comments={[comment()]} />);
    expect(screen.getByText("root comment")).toBeTruthy();
    expect(screen.queryByPlaceholderText("Add a comment…")).toBeNull();
    expect(screen.queryByText("Reply")).toBeNull();
    expect(screen.queryByText("Mark complete")).toBeNull();
  });

  it("Mark complete PUTs the toggled value; completed text renders struck-through", async () => {
    api.mockResolvedValue({ data: { ok: true } });
    render(<CommentPanel {...base} comments={[comment({ completed: true, text: "done item" })]} />);
    expect(screen.getByText("done item").className).toContain("line-through");
    fireEvent.click(screen.getByText("Reopen"));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(String(api.mock.calls[0]?.[0])).toBe("/orgs/o-1/comments/c-1/completed");
    expect(posted()).toEqual({ completed: false }); // toggled off
  });
});

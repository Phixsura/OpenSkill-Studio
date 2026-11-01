import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CollabThreadList } from "@/components/collab-thread-list";

const threads = [
  { threadId: "t1", title: "API Design", authorId: "dev-1", status: "open", tags: ["api"], messageCount: 5, createdAt: Date.now() },
  { threadId: "t2", title: "Bug Report", authorId: "dev-2", status: "resolved", tags: [], messageCount: 3, createdAt: Date.now() },
];

describe("CollabThreadList", () => {
  it("renders threads", () => {
    const { container } = render(<CollabThreadList threads={threads} />);
    expect(container.textContent).toContain("API Design");
    expect(container.textContent).toContain("5 messages");
    expect(container.textContent).toContain("resolved");
  });
  it("select thread", () => {
    const fn = vi.fn();
    const { container } = render(<CollabThreadList threads={threads} onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]); // first thread (btns[0] is New Thread)
    expect(fn).toHaveBeenCalledWith("t1");
  });
});

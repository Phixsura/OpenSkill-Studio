import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommunityForumPanel } from "@/components/community-forum-panel";

const threads = [
  { threadId: "t1", title: "How to deploy?", author: "alice", tags: ["deploy"],
    replyCount: 5, upvotes: 12, answered: true, timestamp: "2h ago" },
  { threadId: "t2", title: "Auth help", author: "bob", tags: ["auth"],
    replyCount: 0, upvotes: 3, answered: false, timestamp: "1h ago" },
];

describe("CommunityForumPanel", () => {
  it("renders threads", () => {
    const { container } = render(<CommunityForumPanel threads={threads} />);
    expect(container.textContent).toContain("How to deploy?");
    expect(container.textContent).toContain("Answered");
    expect(container.textContent).toContain("💬 5");
  });
  it("calls onUpvote", () => {
    const fn = vi.fn();
    const { container } = render(<CommunityForumPanel threads={threads} onUpvote={fn} />);
    const upBtn = container.querySelector("button");
    if (upBtn) fireEvent.click(upBtn);
    expect(fn).toHaveBeenCalledWith("t1");
  });
});

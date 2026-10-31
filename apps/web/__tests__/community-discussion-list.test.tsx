import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommunityDiscussionList } from "@/components/community-discussion-list";

describe("CommunityDiscussionList", () => {
  const discussions = [
    { discussion_id: "d1", title: "How to use webhooks?", category: "help", author_id: "u1",
      replies: 3, upvotes: 5, solved: true, created_at: "2026-10-20" },
  ];
  it("renders", () => {
    const { container } = render(<CommunityDiscussionList discussions={discussions} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Community Discussions");
    expect(container.textContent).toContain("How to use webhooks?");
    expect(container.textContent).toContain("help");
    expect(container.textContent).toContain("💬 3");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(<CommunityDiscussionList discussions={discussions} onSelect={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("d1");
  });
});

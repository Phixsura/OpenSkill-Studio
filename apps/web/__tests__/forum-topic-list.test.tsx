import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ForumTopicList } from "@/components/forum-topic-list";

describe("ForumTopicList", () => {
  it("renders topics", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <ForumTopicList total={2} sort="recent" onSelect={onSelect} topics={[
        { title: "How to use webhooks?", author: "alice", category: "help",
          replies: 3, views: 100, likes: 5, solved: true },
        { title: "Bug report", author: "bob", category: "bugs",
          replies: 0, views: 50, likes: 2, solved: false },
      ]} />
    );
    expect(container.textContent).toContain("Forum");
    expect(container.textContent).toContain("How to use webhooks?");
    expect(container.textContent).toContain("Solved");
    expect(container.textContent).toContain("Bug report");
    fireEvent.click(getByText("How to use webhooks?"));
    expect(onSelect).toHaveBeenCalledWith("How to use webhooks?");
  });
});

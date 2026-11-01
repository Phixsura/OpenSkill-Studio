import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommunityPageLayout } from "@/components/community-page-layout";

describe("CommunityPageLayout", () => {
  it("renders", () => {
    const { container } = render(
      <CommunityPageLayout stats={{ members: 500, online: 25, discussions: 100 }}
        pinned={[{ title: "Welcome!", pinned: true }]} recent={[]}
        categories={["general", "help"]} onNewDiscussion={vi.fn()}>
        <p>Discussions</p>
      </CommunityPageLayout>
    );
    expect(container.textContent).toContain("Community");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("general");
    expect(container.textContent).toContain("Discussions");
  });
  it("new discussion", () => {
    const fn = vi.fn();
    const { container } = render(
      <CommunityPageLayout stats={{ members: 0, online: 0, discussions: 0 }}
        pinned={[]} recent={[]} categories={[]} onNewDiscussion={fn}>
        <p>C</p>
      </CommunityPageLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("New"))!);
    expect(fn).toHaveBeenCalled();
  });
});

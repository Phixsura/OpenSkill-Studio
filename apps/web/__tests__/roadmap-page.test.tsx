import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RoadmapPage } from "@/components/roadmap-page";

describe("RoadmapPage", () => {
  it("renders", () => {
    const { container } = render(
      <RoadmapPage
        inProgress={[{ id: "r1", title: "GraphQL API", description: "New API", eta: "Q4 2026" }]}
        planned={[{ id: "r2", title: "Mobile SDK", description: "Flutter support" }]}
        completed={[{ id: "r0", title: "100K Lines", description: "Done!", completed_at: "2026-10" }]}
        onVote={vi.fn()} />
    );
    expect(container.textContent).toContain("Platform Roadmap");
    expect(container.textContent).toContain("GraphQL API");
    expect(container.textContent).toContain("Mobile SDK");
    expect(container.textContent).toContain("100K Lines");
  });
  it("votes", () => {
    const fn = vi.fn();
    const { container } = render(
      <RoadmapPage inProgress={[{ id: "r1", title: "X", description: "Y" }]}
        planned={[]} completed={[]} onVote={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Vote"))!);
    expect(fn).toHaveBeenCalledWith("r1");
  });
});

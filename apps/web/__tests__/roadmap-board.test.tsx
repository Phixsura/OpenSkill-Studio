import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RoadmapBoard } from "@/components/roadmap-board";

describe("RoadmapBoard", () => {
  it("renders board", () => {
    const onVote = vi.fn();
    const { container, getAllByText } = render(
      <RoadmapBoard statuses={["planned", "in_progress", "shipped"]} onVote={onVote}
        columns={{
          planned: [{ id: "r1", title: "GraphQL", description: "New API", votes: 85, quarter: "", tags: [] }],
          in_progress: [{ id: "r2", title: "SSO", description: "", votes: 42, quarter: "Q4 2026", tags: [] }],
          shipped: [],
        }} />
    );
    expect(container.textContent).toContain("Planned");
    expect(container.textContent).toContain("GraphQL");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("Q4 2026");
    fireEvent.click(getAllByText(/▲/)[0]);
    expect(onVote).toHaveBeenCalledWith("r1");
  });
});

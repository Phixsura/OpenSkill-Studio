import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureRequestBoard } from "@/components/feature-request-board";

describe("FeatureRequestBoard", () => {
  it("renders requests", () => {
    const { container } = render(
      <FeatureRequestBoard total={5} openCount={3} onVote={vi.fn()}
        requests={[
          { id: 1, title: "Dark Mode", category: "ui", votes: 42, status: "open" },
          { id: 2, title: "API v3", category: "api", votes: 28, status: "open" },
        ]} />
    );
    expect(container.textContent).toContain("Feature Requests");
    expect(container.textContent).toContain("3 open");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("API v3");
  });
});

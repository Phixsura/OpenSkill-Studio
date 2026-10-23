import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureRequestBoard } from "@/components/feature-request-board";

describe("FeatureRequestBoard", () => {
  it("renders requests", () => {
    const onVote = vi.fn();
    const { container, getAllByText } = render(
      <FeatureRequestBoard totalVotes={15} onVote={onVote} requests={[
        { id: 1, title: "Dark mode", votes: 10, status: "open", category: "ui" },
        { id: 2, title: "SSO", votes: 5, status: "open", category: "security" },
      ]} />
    );
    expect(container.textContent).toContain("Feature Requests");
    expect(container.textContent).toContain("15 votes");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("10");
    fireEvent.click(getAllByText("▲")[0]);
    expect(onVote).toHaveBeenCalledWith(1);
  });
});

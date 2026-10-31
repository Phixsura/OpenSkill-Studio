import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureRequestBoard } from "@/components/feature-request-board";

const mockRequests = [
  { id: "fr1", title: "Dark Mode", description: "Add dark theme support", author: "alice", votes: 42, status: "planned" as const, hasVoted: true, developerResponse: "Coming in v3.0!" },
  { id: "fr2", title: "Export CSV", description: "Export data as CSV", author: "bob", votes: 15, status: "open" as const, hasVoted: false },
];

describe("FeatureRequestBoard", () => {
  it("renders requests with votes", () => {
    const { container } = render(
      <FeatureRequestBoard requests={mockRequests} extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Feature Requests");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("Planned");
  });

  it("shows developer response", () => {
    const { container } = render(
      <FeatureRequestBoard requests={mockRequests} extensionName="Test" />
    );
    expect(container.textContent).toContain("Coming in v3.0!");
  });

  it("calls onVote", () => {
    const onVote = vi.fn();
    const { container } = render(
      <FeatureRequestBoard requests={mockRequests} extensionName="Test" onVote={onVote} />
    );
    const voteButtons = container.querySelectorAll("button");
    const voteBtn = Array.from(voteButtons).find(b => b.textContent?.includes("15"));
    if (voteBtn) fireEvent.click(voteBtn);
    expect(onVote).toHaveBeenCalledWith("fr2");
  });

  it("shows new request form", () => {
    const { getByText, getByPlaceholderText } = render(
      <FeatureRequestBoard requests={mockRequests} extensionName="Test" />
    );
    fireEvent.click(getByText("+ New Request"));
    expect(getByPlaceholderText("Feature title")).toBeDefined();
  });
});

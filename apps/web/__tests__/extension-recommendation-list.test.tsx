import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionRecommendationList } from "@/components/extension-recommendation-list";

const mockRecs = [
  { id: "r1", name: "Slack Bot Pro", icon: "💬", description: "Advanced Slack integration", rating: 4.8, downloads: 15000, matchScore: 92, reason: "Similar orgs use this" },
  { id: "r2", name: "Analytics Plus", icon: "📊", description: "Deep analytics", rating: 4.5, downloads: 8000, matchScore: 78, reason: "Matches your interests" },
];

describe("ExtensionRecommendationList", () => {
  it("renders recommendations", () => {
    const { container } = render(<ExtensionRecommendationList recommendations={mockRecs} />);
    expect(container.textContent).toContain("Recommended for You");
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("92% match");
    expect(container.textContent).toContain("Similar orgs");
  });

  it("calls onInstall", () => {
    const onInstall = vi.fn();
    const { getAllByText } = render(
      <ExtensionRecommendationList recommendations={mockRecs} onInstall={onInstall} />
    );
    fireEvent.click(getAllByText("Install")[0]);
    expect(onInstall).toHaveBeenCalledWith("r1");
  });

  it("calls onDismiss", () => {
    const onDismiss = vi.fn();
    const { getAllByText } = render(
      <ExtensionRecommendationList recommendations={mockRecs} onDismiss={onDismiss} />
    );
    fireEvent.click(getAllByText("Dismiss")[0]);
    expect(onDismiss).toHaveBeenCalledWith("r1");
  });

  it("renders nothing when empty", () => {
    const { container } = render(<ExtensionRecommendationList recommendations={[]} />);
    expect(container.innerHTML).toBe("");
  });
});

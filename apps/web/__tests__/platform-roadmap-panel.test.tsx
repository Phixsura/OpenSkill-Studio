import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformRoadmapPanel } from "@/components/platform-roadmap-panel";

const items = [
  { itemId: "r1", title: "Dark Mode", description: "Dark theme", status: "planned", category: "ui", votes: 42, eta: "Q1" },
  { itemId: "r2", title: "GraphQL", description: "GraphQL API", status: "in_progress", category: "api", votes: 30, eta: "Q2" },
  { itemId: "r3", title: "SSO", description: "Single sign-on", status: "completed", category: "auth", votes: 100, eta: "" },
];

describe("PlatformRoadmapPanel", () => {
  it("renders columns", () => {
    const { container } = render(<PlatformRoadmapPanel items={items} />);
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("GraphQL");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("Planned");
    expect(container.textContent).toContain("In Progress");
  });
  it("calls onVote", () => {
    const fn = vi.fn();
    const { container } = render(<PlatformRoadmapPanel items={items} onVote={fn} />);
    const voteBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("42"));
    if (voteBtn) fireEvent.click(voteBtn);
    expect(fn).toHaveBeenCalledWith("r1");
  });
});

import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperProfileCard } from "@/components/developer-profile-card";

const mockProfile = {
  id: "dev-1", name: "Alice Chen", avatar: "👩‍💻", bio: "Full-stack dev building tools for developers",
  company: "Acme Inc", website: "alice.dev", joinedAt: "Jan 2025",
  extensionCount: 8, totalDownloads: 45000, avgRating: 4.7, verified: true,
  badges: [
    { name: "Top Publisher", icon: "🏆" },
    { name: "100K Downloads", icon: "⬇️" },
  ],
  topExtensions: [
    { name: "Slack Bot Pro", downloads: 15000, rating: 4.8 },
    { name: "Code Formatter", downloads: 12000, rating: 4.6 },
  ],
};

describe("DeveloperProfileCard", () => {
  it("renders profile details", () => {
    const { container } = render(<DeveloperProfileCard profile={mockProfile} />);
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("Acme Inc");
    expect(container.textContent).toContain("Full-stack dev");
    expect(container.textContent).toContain("45,000");
    expect(container.textContent).toContain("4.7");
  });

  it("shows verified badge and badges", () => {
    const { container } = render(<DeveloperProfileCard profile={mockProfile} />);
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Top Publisher");
    expect(container.textContent).toContain("100K Downloads");
  });

  it("renders top extensions", () => {
    const { container } = render(<DeveloperProfileCard profile={mockProfile} />);
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("15,000");
  });

  it("calls onViewExtensions", () => {
    const onView = vi.fn();
    const { getByText } = render(<DeveloperProfileCard profile={mockProfile} onViewExtensions={onView} />);
    fireEvent.click(getByText("View All Extensions →"));
    expect(onView).toHaveBeenCalled();
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperBadgeShelf } from "@/components/developer-badge-shelf";

describe("DeveloperBadgeShelf", () => {
  const badges = [
    { id: "first_app", label: "First App", icon: "🚀", description: "Published first app", tier: "bronze" },
    { id: "popular", label: "Popular", icon: "🔥", description: "1K installs", tier: "silver" },
  ];
  it("renders", () => {
    const { container } = render(<DeveloperBadgeShelf badges={badges} totalAvailable={7} />);
    expect(container.textContent).toContain("Badges");
    expect(container.textContent).toContain("2/7");
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("First App");
    expect(container.textContent).toContain("Popular");
  });
  it("empty state", () => {
    const { container } = render(<DeveloperBadgeShelf badges={[]} totalAvailable={7} />);
    expect(container.textContent).toContain("No badges yet");
  });
});

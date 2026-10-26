import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformChangelogPanel } from "@/components/platform-changelog-panel";

const releases = [
  { version: "2.0", date: "2024-06-01", title: "Major Update",
    features: ["SDK v2", "Sandbox"], fixes: ["Auth bug"], breaking: ["New API format"] },
  { version: "1.0", date: "2024-01-01", title: "Launch",
    features: ["Core platform"], fixes: [], breaking: [] },
];

describe("PlatformChangelogPanel", () => {
  it("renders releases", () => {
    const { container } = render(<PlatformChangelogPanel releases={releases} />);
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("Major Update");
    expect(container.textContent).toContain("SDK v2");
    expect(container.textContent).toContain("New API format");
    expect(container.textContent).toContain("Auth bug");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIStatusBadgeCard from "../src/components/api-status-badge-card";

const badges = [
  { badge_id: "b1", label: "build", status: "passing", color: "green", views: 100 },
  { badge_id: "b2", label: "coverage", status: "95%", color: "yellow", views: 50 },
];

describe("APIStatusBadgeCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIStatusBadgeCard badges={badges} appName="App" />);
    expect(container.textContent).toContain("Status Badges");
    expect(container.textContent).toContain("2 badges");
  });

  it("shows badge labels and statuses", () => {
    const { container } = render(<APIStatusBadgeCard badges={badges} appName="App" />);
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("passing");
    expect(container.textContent).toContain("95%");
  });

  it("shows empty state", () => {
    const { container } = render(<APIStatusBadgeCard badges={[]} appName="App" />);
    expect(container.textContent).toContain("No status badges");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadgeCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-developer-api-status-badge-card";

const badges = [
  { badge_id: "uptime", label: "uptime", value: "99.99%", color: "green" },
  { badge_id: "build", label: "build", value: "passing", color: "green" },
];

describe("Card", () => {
  it("shows badges", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadgeCard badges={badges} appName="App" />);
    expect(container.textContent).toContain("Status Badges");
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("passing");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadgeCard badges={[]} appName="App" />);
    expect(container.textContent).toContain("No badges");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortemCard from "../src/components/api-developer-api-api-developer-api-api-platform-incident-postmortem-card";

const postmortems = [{ postmortem_id: "pm1", title: "Database Outage", severity: "sev1", root_cause: "Connection pool exhausted", status: "published", action_item_count: 3, duration_minutes: 45 }];

describe("Card", () => {
  it("shows postmortems", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortemCard postmortems={postmortems} severityCounts={{ sev1: 1 }} appName="App" />);
    expect(container.textContent).toContain("Postmortems");
    expect(container.textContent).toContain("Database Outage");
    expect(container.textContent).toContain("sev1");
    expect(container.textContent).toContain("45m");
    expect(container.textContent).toContain("Connection pool exhausted");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortemCard postmortems={[]} severityCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No postmortems");
  });
});

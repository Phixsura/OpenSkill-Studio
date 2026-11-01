import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-incident-tracker-card";

describe("ConsumerIncidentTrackerCard", () => {
  it("shows incidents", () => {
    const incidents = [{ id: "i1", title: "DB Outage", severity: "critical", status: "investigating", affectedEndpoints: ["/api/users"], createdAt: "12:00" }];
    const { container } = render(<Card incidents={incidents} appName="App" />);
    expect(container.textContent).toContain("Incidents");
    expect(container.textContent).toContain("DB Outage");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("investigating");
  });
  it("shows all clear", () => {
    const { container } = render(<Card incidents={[]} appName="App" />);
    expect(container.textContent).toContain("All systems operational");
  });
});

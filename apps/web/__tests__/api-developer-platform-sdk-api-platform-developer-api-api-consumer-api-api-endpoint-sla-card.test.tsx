import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-sla-card";

describe("EndpointSlaCard", () => {
  it("shows SLAs", () => {
    const slas = [{ endpoint: "/api", method: "GET", meeting_sla: true, actual_uptime: 99.95, target_uptime: 99.9, actual_p99: 200, target_p99: 500, violations: [] }];
    const { container } = render(<Card slas={slas} violationCount={0} appName="App" />);
    expect(container.textContent).toContain("Endpoint SLAs");
    expect(container.textContent).toContain("GET /api");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows violations", () => {
    const { container } = render(<Card slas={[]} violationCount={3} appName="App" />);
    expect(container.textContent).toContain("3 violations");
  });
});

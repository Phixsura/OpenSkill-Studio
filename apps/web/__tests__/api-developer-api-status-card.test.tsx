import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIStatusCard from "../src/components/api-developer-api-status-card";

const statuses = [
  { service_name: "API", status: "operational", response_time_ms: 45 },
  { service_name: "Database", status: "degraded", response_time_ms: 200 },
];

describe("APIDeveloperAPIStatusCard", () => {
  it("shows status", () => {
    const { container } = render(<APIDeveloperAPIStatusCard statuses={statuses} overallStatus="degraded" appName="App" />);
    expect(container.textContent).toContain("API Status");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("45ms");
  });
});

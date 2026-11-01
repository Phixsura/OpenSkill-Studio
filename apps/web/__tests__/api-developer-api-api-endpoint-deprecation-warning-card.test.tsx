import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiEndpointDeprecationWarningCard from "../src/components/api-developer-api-api-endpoint-deprecation-warning-card";

const warnings = [
  { endpoint: "/api/v1/users", method: "GET", replacement: "/api/v2/users", sunset_date: "2025-06-01", consumers_warned_count: 5, total_warnings_sent: 150 },
];

describe("APIDeveloperAPIApiEndpointDeprecationWarningCard", () => {
  it("shows warnings", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointDeprecationWarningCard warnings={warnings} appName="App" />);
    expect(container.textContent).toContain("Deprecation Warnings");
    expect(container.textContent).toContain("GET /api/v1/users");
    expect(container.textContent).toContain("/api/v2/users");
    expect(container.textContent).toContain("sunset: 2025-06-01");
    expect(container.textContent).toContain("150 warnings");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointDeprecationWarningCard warnings={[]} appName="App" />);
    expect(container.textContent).toContain("No deprecation warnings");
  });
});

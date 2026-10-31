import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTrackerCard from "../src/components/api-developer-api-api-developer-api-api-endpoint-response-schema-tracker-card";

const schemas = [
  { endpoint: "/api/users", method: "GET", has_drift: true, missing_fields: ["email"], extra_fields: ["avatar"], drift_count: 5 },
  { endpoint: "/api/orders", method: "GET", has_drift: false, missing_fields: [], extra_fields: [], drift_count: 0 },
];

describe("APIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTrackerCard", () => {
  it("shows schema drift", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTrackerCard schemas={schemas} driftedCount={1} appName="App" />);
    expect(container.textContent).toContain("Schema Drift");
    expect(container.textContent).toContain("1 drifted");
    expect(container.textContent).toContain("-email");
    expect(container.textContent).toContain("+avatar");
  });
  it("shows in sync", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTrackerCard schemas={[]} driftedCount={0} appName="App" />);
    expect(container.textContent).toContain("in sync");
  });
});

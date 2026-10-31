import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-canary-card";

describe("RequestCanaryCard", () => {
  it("shows canaries", () => {
    const canaries = [{ canary_id: "c1", endpoint: "/api/v2", canary_pct: 10, canary_error_rate: 2, should_rollback: false, canary_requests: 100, stable_requests: 900 }];
    const { container } = render(<Card canaries={canaries} appName="App" />);
    expect(container.textContent).toContain("Canary Deployments");
    expect(container.textContent).toContain("/api/v2");
    expect(container.textContent).toContain("10% canary");
  });
  it("shows rollback warning", () => {
    const canaries = [{ canary_id: "c1", endpoint: "/api", canary_pct: 10, canary_error_rate: 25, should_rollback: true, canary_requests: 50, stable_requests: 450 }];
    const { container } = render(<Card canaries={canaries} appName="App" />);
    expect(container.textContent).toContain("ROLLBACK");
  });
});

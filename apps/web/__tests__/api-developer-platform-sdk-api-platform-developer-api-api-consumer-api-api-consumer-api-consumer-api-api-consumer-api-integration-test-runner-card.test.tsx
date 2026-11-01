import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-integration-test-runner-card";

describe("ConsumerApiIntegrationTestRunnerCard", () => {
  it("shows runs", () => {
    const runs = [{ id: "r1", passed: 5, failed: 0, total: 5, runAt: "12:00" }];
    const { container } = render(<Card runs={runs} suiteCount={2} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Integration Tests");
    expect(container.textContent).toContain("All tests passed");
    expect(container.textContent).toContain("5/5");
  });
  it("shows empty", () => {
    const { container } = render(<Card runs={[]} suiteCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No test runs");
  });
});

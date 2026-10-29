import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunnerCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-integration-test-runner-card";

const runs = [
  { run_id: "r1", suite_name: "Auth Suite", total: 10, passed: 10, failed: 0, pass_rate: 100, all_passed: true },
  { run_id: "r2", suite_name: "Payment Suite", total: 8, passed: 6, failed: 2, pass_rate: 75, all_passed: false },
];

describe("Card", () => {
  it("shows test runs", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunnerCard runs={runs} failingCount={1} appName="App" />);
    expect(container.textContent).toContain("Integration Tests");
    expect(container.textContent).toContain("1 failing");
    expect(container.textContent).toContain("Auth Suite");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("75%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunnerCard runs={[]} failingCount={0} appName="App" />);
    expect(container.textContent).toContain("No test runs");
  });
});

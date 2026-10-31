import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiLoadTestRunnerCard from "../src/components/api-developer-api-api-load-test-runner-card";

const results = [
  { test_id: "t1", endpoint: "/api/users", concurrency: 100, rps: 500, success_rate: 99.9, avg_latency_ms: 45, p99_latency_ms: 200, passed: true },
  { test_id: "t2", endpoint: "/api/heavy", concurrency: 50, rps: 50, success_rate: 80, avg_latency_ms: 500, p99_latency_ms: 2000, passed: false },
];

describe("APIDeveloperAPIApiLoadTestRunnerCard", () => {
  it("shows load tests", () => {
    const { container } = render(<APIDeveloperAPIApiLoadTestRunnerCard results={results} failingCount={1} appName="App" />);
    expect(container.textContent).toContain("Load Tests");
    expect(container.textContent).toContain("1 failing");
    expect(container.textContent).toContain("PASS");
    expect(container.textContent).toContain("FAIL");
    expect(container.textContent).toContain("500 rps");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiLoadTestRunnerCard results={[]} failingCount={0} appName="App" />);
    expect(container.textContent).toContain("No load tests");
  });
});

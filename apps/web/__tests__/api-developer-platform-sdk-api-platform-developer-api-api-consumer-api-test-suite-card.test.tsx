import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-test-suite-card";

describe("TestSuiteCard", () => {
  it("shows runs", () => {
    const runs = [{ run_id: "r1", consumer_id: "c1", status: "passed", pass_count: 5, fail_count: 0, total_tests: 5 }];
    const { container } = render(<Card runs={runs} appName="App" />);
    expect(container.textContent).toContain("Test Suites");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("/ 5");
  });
  it("shows empty", () => {
    const { container } = render(<Card runs={[]} appName="App" />);
    expect(container.textContent).toContain("No test runs");
  });
});

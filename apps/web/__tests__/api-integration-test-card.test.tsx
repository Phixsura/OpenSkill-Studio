import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIIntegrationTestCard from "../src/components/api-integration-test-card";

const tests = [
  { test_id: "t1", name: "Auth Flow", pass_count: 3, fail_count: 0, total_steps: 3, passed: true },
  { test_id: "t2", name: "CRUD Cycle", pass_count: 2, fail_count: 1, total_steps: 3, passed: false },
];

describe("APIIntegrationTestCard", () => {
  it("renders header and pass count", () => {
    const { container } = render(<APIIntegrationTestCard tests={tests} appName="App" />);
    expect(container.textContent).toContain("Integration Tests");
    expect(container.textContent).toContain("1/2 passed");
  });

  it("shows test names and steps", () => {
    const { container } = render(<APIIntegrationTestCard tests={tests} appName="App" />);
    expect(container.textContent).toContain("Auth Flow");
    expect(container.textContent).toContain("3/3 steps");
    expect(container.textContent).toContain("2/3 steps");
  });

  it("shows empty state", () => {
    const { container } = render(<APIIntegrationTestCard tests={[]} appName="App" />);
    expect(container.textContent).toContain("No integration tests");
  });
});

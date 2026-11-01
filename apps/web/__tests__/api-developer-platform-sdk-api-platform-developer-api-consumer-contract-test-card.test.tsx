import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-contract-test-card";

describe("ContractTestCard", () => {
  it("shows tests", () => {
    const tests = [{ test_id: "t1", endpoint: "/users", method: "GET", last_result: "passed" }];
    const { container } = render(<Card consumerId="c1" tests={tests} passRate={100} appName="App" />);
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("passed");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" tests={[]} passRate={0} appName="App" />);
    expect(container.textContent).toContain("No contract tests");
  });
});

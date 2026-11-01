import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APITestSuiteCard from "../src/components/api-test-suite-card";

const suites = [
  {
    suite_id: "s1",
    name: "User API",
    pass_rate: 50.0,
    tests: [
      {
        test_id: "t1",
        name: "List Users",
        method: "GET",
        path: "/users",
        result: "passed" as const,
      },
      {
        test_id: "t2",
        name: "Create User",
        method: "POST",
        path: "/users",
        result: "failed" as const,
      },
    ],
  },
];

describe("APITestSuiteCard", () => {
  it("renders header and suite count", () => {
    const { container } = render(<APITestSuiteCard suites={suites} appName="App" />);
    expect(container.textContent).toContain("API Test Suites");
    expect(container.textContent).toContain("1 suites");
  });

  it("shows suite name and pass rate", () => {
    const { container } = render(<APITestSuiteCard suites={suites} appName="App" />);
    expect(container.textContent).toContain("User API");
    expect(container.textContent).toContain("50% pass");
  });

  it("shows test names", () => {
    const { container } = render(<APITestSuiteCard suites={suites} appName="App" />);
    expect(container.textContent).toContain("List Users");
    expect(container.textContent).toContain("Create User");
  });

  it("shows empty state", () => {
    const { container } = render(<APITestSuiteCard suites={[]} appName="App" />);
    expect(container.textContent).toContain("No test suites");
  });
});

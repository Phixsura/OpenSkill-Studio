import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiTestResults } from "@/components/api-test-results";

describe("ApiTestResults", () => {
  const results = [
    { name: "List apps", method: "GET", path: "/api/apps", expectedStatus: 200, actualStatus: 200, passed: true, durationMs: 45 },
    { name: "Bad auth", method: "GET", path: "/api/me", expectedStatus: 200, actualStatus: 401, passed: false, durationMs: 10 },
  ];
  it("renders results", () => {
    const { container } = render(
      <ApiTestResults results={results} passed={1} failed={1} passRate={50} totalMs={55} allPassed={false} />
    );
    expect(container.textContent).toContain("API Tests");
    expect(container.textContent).toContain("1 passed");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("List apps");
    expect(container.textContent).toContain("401 ≠ 200");
  });
});

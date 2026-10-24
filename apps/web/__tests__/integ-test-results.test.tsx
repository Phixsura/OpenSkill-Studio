import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IntegTestResults } from "@/components/integ-test-results";

describe("IntegTestResults", () => {
  it("renders results", () => {
    const { container } = render(
      <IntegTestResults suite="API Tests" passed={2} failed={1} passRate={67} durationMs={330}
        results={[
          { name: "login", status: "passed", durationMs: 50, error: "" },
          { name: "checkout", status: "failed", durationMs: 200, error: "timeout" },
        ]} />
    );
    expect(container.textContent).toContain("API Tests");
    expect(container.textContent).toContain("2 passed");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("login");
    expect(container.textContent).toContain("timeout");
  });
});

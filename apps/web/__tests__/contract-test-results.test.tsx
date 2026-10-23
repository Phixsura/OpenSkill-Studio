import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractTestResults } from "@/components/contract-test-results";

describe("ContractTestResults", () => {
  it("renders results", () => {
    const { container } = render(
      <ContractTestResults total={2} passed={1} failed={1} passRate={50} allPassed={false}
        results={[
          { name: "GET /users", valid: true, errors: [] },
          { name: "GET /bad", valid: false, errors: [{ field: "status", error: "mismatch" }] },
        ]} />
    );
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1/2 passed");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("GET /bad");
    expect(container.textContent).toContain("status: mismatch");
  });
});

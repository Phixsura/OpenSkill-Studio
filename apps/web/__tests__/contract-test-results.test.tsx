import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractTestResults } from "@/components/contract-test-results";

describe("ContractTestResults", () => {
  it("renders results", () => {
    const results = [
      { endpoint: "/users", valid: true, errors: [] },
      { endpoint: "/apps", valid: false, errors: ["Missing field: id"] },
    ];
    const { container } = render(<ContractTestResults results={results} passRate={50} />);
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("Missing field: id");
    expect(container.textContent).toContain("50%");
  });
});

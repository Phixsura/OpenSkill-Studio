import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractTestResults } from "@/components/contract-test-results";

describe("ContractTestResults", () => {
  it("renders results", () => {
    const { container } = render(
      <ContractTestResults passRate={67} passed={2} failed={1}
        results={[
          { contractName: "get_user", valid: true, errorCount: 0, fieldsChecked: 5 },
          { contractName: "create_order", valid: true, errorCount: 0, fieldsChecked: 3 },
          { contractName: "delete_user", valid: false, errorCount: 2, fieldsChecked: 4 },
        ]} />
    );
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("2 passed");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("get_user");
    expect(container.textContent).toContain("delete_user");
  });
});

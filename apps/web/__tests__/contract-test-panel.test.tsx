import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractTestPanel } from "@/components/contract-test-panel";
describe("ContractTestPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ContractTestPanel passed={1} failed={1}
        results={[
          { name: "get_user", valid: true, errors: 0 },
          { name: "create_order", valid: false, errors: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("1/2 passed");
    expect(container.textContent).toContain("get_user");
    expect(container.textContent).toContain("create_order");
    expect(container.textContent).toContain("2 errors");
  });
});

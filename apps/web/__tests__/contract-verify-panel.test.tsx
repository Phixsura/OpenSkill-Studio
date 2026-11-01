import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractVerifyPanel } from "@/components/contract-verify-panel";
describe("ContractVerifyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ContractVerifyPanel allCompatible={false} compatible={1} total={2}
        results={[
          { producer: "user-svc", consumer: "order-svc", compatible: true, missingFields: [] },
          { producer: "user-svc", consumer: "billing", compatible: false, missingFields: ["email"] },
        ]} />
    );
    expect(container.textContent).toContain("Contract Verification");
    expect(container.textContent).toContain("1/2 compatible");
    expect(container.textContent).toContain("user-svc → order-svc");
    expect(container.textContent).toContain("user-svc → billing");
    expect(container.textContent).toContain("missing: email");
  });
});

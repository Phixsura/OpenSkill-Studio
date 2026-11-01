import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractRegBrowser } from "@/components/contract-reg-browser";

describe("ContractRegBrowser", () => {
  it("renders contracts", () => {
    const { container } = render(
      <ContractRegBrowser total={3} providers={["user-svc", "order-svc"]}
        contracts={[
          { contractId: "abc123", provider: "user-svc", consumer: "api-gw", version: "1.0", fieldCount: 5, status: "active" },
          { contractId: "def456", provider: "order-svc", consumer: "api-gw", version: "2.0", fieldCount: 8, status: "active" },
        ]} />
    );
    expect(container.textContent).toContain("Contract Registry");
    expect(container.textContent).toContain("3 contracts");
    expect(container.textContent).toContain("2 providers");
    expect(container.textContent).toContain("user-svc");
    expect(container.textContent).toContain("api-gw");
    expect(container.textContent).toContain("5 fields");
  });
});

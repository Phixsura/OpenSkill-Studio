import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContractRegPanel } from "@/components/contract-reg-panel";
describe("ContractRegPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ContractRegPanel totalVersions={5}
        contracts={[
          { name: "user-api", versions: 3, latest: "3.0" },
          { name: "order-api", versions: 2, latest: "2.0" },
        ]} />
    );
    expect(container.textContent).toContain("Contract Registry");
    expect(container.textContent).toContain("2 contracts");
    expect(container.textContent).toContain("5 versions");
    expect(container.textContent).toContain("user-api");
    expect(container.textContent).toContain("v3.0");
  });
});

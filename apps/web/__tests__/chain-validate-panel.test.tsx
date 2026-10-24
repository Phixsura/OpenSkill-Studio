import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChainValidatePanel } from "@/components/chain-validate-panel";
describe("ChainValidatePanel", () => {
  it("renders cycle", () => {
    const { container } = render(
      <ChainValidatePanel valid={false} maxDepth={3} services={3} depthLimit={10}
        cycles={[["a", "b", "c", "a"]]} />
    );
    expect(container.textContent).toContain("Chain Validator");
    expect(container.textContent).toContain("Invalid");
    expect(container.textContent).toContain("Cycle: a → b → c → a");
  });
});

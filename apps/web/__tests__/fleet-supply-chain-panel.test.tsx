import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSupplyChainPanel } from "@/components/fleet-supply-chain-panel";
describe("FleetSupplyChainPanel", () => { it("renders", () => {
    const { container } = render(<FleetSupplyChainPanel total={20} withSbom={15} signed={18} secure={false} />);
    expect(container.textContent).toContain("Supply Chain");
    expect(container.textContent).toContain("Incomplete");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSupplyChainV9Panel } from "@/components/fleet-supply-chain-v9-panel";
describe("FleetSupplyChainV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSupplyChainV9Panel artifacts={500} signed={500} />);
    expect(container.textContent).toContain("Supply Chain v9");
}); });

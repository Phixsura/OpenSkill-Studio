import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContractPanel } from "@/components/fleet-contract-panel";
describe("FleetContractPanel", () => { it("renders", () => {
    const { container } = render(<FleetContractPanel total={10} passing={9} broken={1} compatible={false} />);
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("1 broken");
}); });

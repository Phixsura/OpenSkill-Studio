import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContractTstPanel } from "@/components/fleet-ai-contract-tst-panel";
describe("FleetAiContractTstPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContractTstPanel testers={4} active={4} contracts={200} verified={20000} breaking={0} />);
    expect(container.textContent).toContain("Contract Test");
}); });

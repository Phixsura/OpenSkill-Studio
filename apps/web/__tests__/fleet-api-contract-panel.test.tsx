import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiContractPanel } from "@/components/fleet-api-contract-panel";
describe("FleetApiContractPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiContractPanel total={30} valid={28} invalid={2} allValid={false} />);
    expect(container.textContent).toContain("API Contracts");
    expect(container.textContent).toContain("2 invalid");
}); });

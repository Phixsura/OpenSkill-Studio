import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiContractV9Panel } from "@/components/fleet-api-contract-v9-panel";
describe("FleetApiContractV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiContractV9Panel contracts={50} breaking={0} />);
    expect(container.textContent).toContain("API Contract v9");
}); });

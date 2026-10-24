import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContractTestV9Panel } from "@/components/fleet-contract-test-v9-panel";
describe("FleetContractTestV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContractTestV9Panel contracts={50} broken={0} />);
    expect(container.textContent).toContain("Contract Test v9");
}); });

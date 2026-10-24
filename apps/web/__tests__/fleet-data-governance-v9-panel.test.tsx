import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataGovernanceV9Panel } from "@/components/fleet-data-governance-v9-panel";
describe("FleetDataGovernanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataGovernanceV9Panel datasets={100} pii={10} />);
    expect(container.textContent).toContain("Data Governance v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDuplicationPanel } from "@/components/fleet-duplication-panel";
describe("FleetDuplicationPanel", () => { it("renders", () => {
    const { container } = render(<FleetDuplicationPanel duplicationPct={8} clones={50} acceptable={false} />);
    expect(container.textContent).toContain("Code Duplication");
    expect(container.textContent).toContain("50 clones");
}); });

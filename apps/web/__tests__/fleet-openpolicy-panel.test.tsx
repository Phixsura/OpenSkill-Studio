import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpenpolicyPanel } from "@/components/fleet-openpolicy-panel";
describe("FleetOpenpolicyPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpenpolicyPanel total={20} withPolicy={16} ciEnforced={14} coveragePct={80} />);
    expect(container.textContent).toContain("Policy-as-Code");
    expect(container.textContent).toContain("80%");
}); });

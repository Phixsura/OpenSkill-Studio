import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRetentionPanel } from "@/components/fleet-retention-panel";
describe("FleetRetentionPanel", () => { it("renders", () => {
    const { container } = render(<FleetRetentionPanel total={10} compliant={8} overdue={2} allCompliant={false} />);
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("2 datasets overdue");
}); });

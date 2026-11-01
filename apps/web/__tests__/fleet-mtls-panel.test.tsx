import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMtlsPanel } from "@/components/fleet-mtls-panel";
describe("FleetMtlsPanel", () => { it("renders", () => {
    const { container } = render(<FleetMtlsPanel total={3} mtlsEnabled={2} pct={66.7} fullCoverage={false} />);
    expect(container.textContent).toContain("mTLS Coverage");
    expect(container.textContent).toContain("66.7%");
}); });

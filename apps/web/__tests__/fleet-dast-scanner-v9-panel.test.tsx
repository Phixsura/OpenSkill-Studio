import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDastScannerV9Panel } from "@/components/fleet-dast-scanner-v9-panel";
describe("FleetDastScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDastScannerV9Panel scans={30} vulns={0} />);
    expect(container.textContent).toContain("DAST Scanner v9");
}); });

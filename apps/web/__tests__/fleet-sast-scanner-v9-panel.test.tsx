import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSastScannerV9Panel } from "@/components/fleet-sast-scanner-v9-panel";
describe("FleetSastScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSastScannerV9Panel scans={50} critical={0} />);
    expect(container.textContent).toContain("SAST Scanner v9");
}); });

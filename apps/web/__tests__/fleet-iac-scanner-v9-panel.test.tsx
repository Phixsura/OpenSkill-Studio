import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIacScannerV9Panel } from "@/components/fleet-iac-scanner-v9-panel";
describe("FleetIacScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIacScannerV9Panel scans={100} critical={0} />);
    expect(container.textContent).toContain("IaC Scanner v9");
}); });

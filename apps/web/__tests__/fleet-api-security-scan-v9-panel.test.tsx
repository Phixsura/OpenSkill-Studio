import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSecurityScanV9Panel } from "@/components/fleet-api-security-scan-v9-panel";
describe("FleetApiSecurityScanV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSecurityScanV9Panel scans={50} findings={0} />);
    expect(container.textContent).toContain("API Security Scan v9");
}); });

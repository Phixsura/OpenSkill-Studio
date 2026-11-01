import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCompScanPanel } from "@/components/fleet-ai-comp-scan-panel";
describe("FleetAiCompScanPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCompScanPanel scanners={4} active={4} scans={5000} violations={50} autoFixed={50} />);
    expect(container.textContent).toContain("Compliance Scanner");
}); });

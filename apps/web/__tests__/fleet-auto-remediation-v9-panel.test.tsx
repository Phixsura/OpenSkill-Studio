import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAutoRemediationV9Panel } from "@/components/fleet-auto-remediation-v9-panel";
describe("FleetAutoRemediationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAutoRemediationV9Panel rules={30} triggered={10} />);
    expect(container.textContent).toContain("Auto Remediation v9");
}); });

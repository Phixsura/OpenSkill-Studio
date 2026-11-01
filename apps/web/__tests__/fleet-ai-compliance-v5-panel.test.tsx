import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiComplianceV5Panel } from "@/components/fleet-ai-compliance-v5-panel";
describe("FleetAiComplianceV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiComplianceV5Panel frameworks={5} active={5} certs={["SOC2", "GDPR"]} controls={2000} compliance={99.8} />);
    expect(container.textContent).toContain("Compliance v5");
}); });

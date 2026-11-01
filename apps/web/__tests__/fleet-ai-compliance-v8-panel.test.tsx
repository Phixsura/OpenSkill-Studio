import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiComplianceV8Panel } from "@/components/fleet-ai-compliance-v8-panel";
describe("FleetAiComplianceV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiComplianceV8Panel frameworks={5} active={5} certs={["SOC2", "GDPR"]} controls={5000} compliance={99.9} />);
    expect(container.textContent).toContain("Compliance v8");
}); });

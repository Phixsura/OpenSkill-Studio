import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiComplianceGovV7Panel } from "@/components/fleet-ai-compliance-gov-v7-panel";
describe("FleetAiComplianceGovV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiComplianceGovV7Panel frameworks={5} active={5} regulations={100} controls={2000} passed={100} score={99.5} />);
    expect(container.textContent).toContain("Compliance Gov v7");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPartnerV7Panel } from "@/components/fleet-ai-partner-v7-panel";
describe("FleetAiPartnerV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPartnerV7Panel systems={3} active={3} partners={1000} integrations={5000} revenue={35} />);
    expect(container.textContent).toContain("Partner v7");
}); });

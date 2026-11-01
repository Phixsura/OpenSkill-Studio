import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGovV5Panel } from "@/components/fleet-ai-gov-v5-panel";
describe("FleetAiGovV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGovV5Panel frameworks={5} active={5} policies={2000} approvals={1000} compliance={99.9} />);
    expect(container.textContent).toContain("Governance v5");
}); });

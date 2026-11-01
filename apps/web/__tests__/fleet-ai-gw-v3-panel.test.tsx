import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGwV3Panel } from "@/components/fleet-ai-gw-v3-panel";
describe("FleetAiGwV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGwV3Panel gateways={3} active={3} providers={15} requests={5000000000} costSaved={40} />);
    expect(container.textContent).toContain("AI Gateway v3");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAbTestPanel } from "@/components/fleet-ai-ab-test-panel";
describe("FleetAiAbTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAbTestPanel tests={10} running={3} concluded={7} impressions={5000000} winners={5} />);
    expect(container.textContent).toContain("A/B Testing");
}); });

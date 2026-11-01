import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpansionV7Panel } from "@/components/fleet-ai-expansion-v7-panel";
describe("FleetAiExpansionV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpansionV7Panel trackers={3} active={3} markets={20} features={200} expansion={200000000} />);
    expect(container.textContent).toContain("Expansion v7");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiKgPanel } from "@/components/fleet-ai-kg-panel";
describe("FleetAiKgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiKgPanel graphs={5} active={5} entities={5000000} relationships={25000000} queries={2000000} />);
    expect(container.textContent).toContain("Knowledge Graph");
}); });

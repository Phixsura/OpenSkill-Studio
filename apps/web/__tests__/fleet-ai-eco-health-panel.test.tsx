import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEcoHealthPanel } from "@/components/fleet-ai-eco-health-panel";
describe("FleetAiEcoHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEcoHealthPanel monitors={3} active={3} plugins={1000} integrations={500} community={500000} growth={30} />);
    expect(container.textContent).toContain("Ecosystem Health");
}); });

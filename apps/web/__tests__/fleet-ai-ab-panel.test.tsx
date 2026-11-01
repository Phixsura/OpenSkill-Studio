import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAbPanel } from "@/components/fleet-ai-ab-panel";
describe("FleetAiAbPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAbPanel experiments={20} active={10} users={500000} winners={8} />);
    expect(container.textContent).toContain("AI A/B Testing");
}); });

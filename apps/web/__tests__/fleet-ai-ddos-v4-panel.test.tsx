import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDdosV4Panel } from "@/components/fleet-ai-ddos-v4-panel";
describe("FleetAiDdosV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDdosV4Panel systems={3} active={3} attacks={500} peak={10} uptime={99.9999} />);
    expect(container.textContent).toContain("AI DDoS v4");
}); });

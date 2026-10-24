import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDdosPanel } from "@/components/fleet-ai-ddos-panel";
describe("FleetAiDdosPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDdosPanel systems={3} active={3} attacks={100} peakGbps={1000} uptime={99.999} />);
    expect(container.textContent).toContain("DDoS Protection");
}); });

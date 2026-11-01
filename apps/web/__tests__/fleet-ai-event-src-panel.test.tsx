import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEventSrcPanel } from "@/components/fleet-ai-event-src-panel";
describe("FleetAiEventSrcPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEventSrcPanel stores={3} active={3} events={500000000} streams={50000} projections={100} />);
    expect(container.textContent).toContain("Event Sourcing");
}); });

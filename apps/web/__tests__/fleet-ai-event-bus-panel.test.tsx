import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEventBusPanel } from "@/components/fleet-ai-event-bus-panel";
describe("FleetAiEventBusPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEventBusPanel buses={3} active={3} events={500000000} subscribers={1000} topics={200} />);
    expect(container.textContent).toContain("Event Bus");
}); });

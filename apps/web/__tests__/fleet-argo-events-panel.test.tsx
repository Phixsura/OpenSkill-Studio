import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgoEventsPanel } from "@/components/fleet-argo-events-panel";
describe("FleetArgoEventsPanel", () => { it("renders", () => {
    const { container } = render(<FleetArgoEventsPanel total={10} active={9} triggers={5000} failed={3} reliable={false} />);
    expect(container.textContent).toContain("Argo Events");
    expect(container.textContent).toContain("3 failed");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiEventStreamV9Panel } from "@/components/fleet-api-event-stream-v9-panel";
describe("FleetApiEventStreamV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiEventStreamV9Panel streams={20} eps={100000} />);
    expect(container.textContent).toContain("Event Stream v9");
}); });

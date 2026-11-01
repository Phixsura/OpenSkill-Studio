import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSsePanel } from "@/components/fleet-sse-panel";
describe("FleetSsePanel", () => { it("renders", () => {
    const { container } = render(<FleetSsePanel streams={5} activeConns={800} eventsPerSec={13000} highVolume={true} />);
    expect(container.textContent).toContain("SSE Streams");
    expect(container.textContent).toContain("High volume");
}); });

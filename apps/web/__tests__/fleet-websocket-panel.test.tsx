import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWebsocketPanel } from "@/components/fleet-websocket-panel";
describe("FleetWebsocketPanel", () => { it("renders", () => {
    const { container } = render(<FleetWebsocketPanel connections={800} maxConnections={1000} utilPct={80} errorsPerMin={0} healthy={true} />);
    expect(container.textContent).toContain("WebSocket");
    expect(container.textContent).toContain("800");
}); });

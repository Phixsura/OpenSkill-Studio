import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiWebsocketV9Panel } from "@/components/fleet-api-websocket-v9-panel";
describe("FleetApiWebsocketV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiWebsocketV9Panel endpoints={20} connections={10000} />);
    expect(container.textContent).toContain("API WebSocket v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiWebsocketAuthV9Panel } from "@/components/fleet-api-websocket-auth-v9-panel";
describe("FleetApiWebsocketAuthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiWebsocketAuthV9Panel connections={5000} authenticated={5000} />);
    expect(container.textContent).toContain("WS Auth v9");
}); });

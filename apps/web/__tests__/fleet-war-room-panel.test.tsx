import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWarRoomPanel } from "@/components/fleet-war-room-panel";
describe("FleetWarRoomPanel", () => { it("renders", () => {
    const { container } = render(<FleetWarRoomPanel total={5} active={1} resolved={4} avgDuration={45} calm={false} />);
    expect(container.textContent).toContain("War Rooms");
    expect(container.textContent).toContain("1 active");
}); });

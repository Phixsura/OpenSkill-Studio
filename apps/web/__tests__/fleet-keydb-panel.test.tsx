import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKeydbPanel } from "@/components/fleet-keydb-panel";
describe("FleetKeydbPanel", () => { it("renders", () => {
    const { container } = render(<FleetKeydbPanel nodes={6} online={6} keys={30000000} opsPerSec={3000000} />);
    expect(container.textContent).toContain("KeyDB");
}); });

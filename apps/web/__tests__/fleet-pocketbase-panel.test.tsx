import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPocketbasePanel } from "@/components/fleet-pocketbase-panel";
describe("FleetPocketbasePanel", () => { it("renders", () => {
    const { container } = render(<FleetPocketbasePanel instances={5} running={5} collections={50} records={500000} />);
    expect(container.textContent).toContain("PocketBase");
}); });

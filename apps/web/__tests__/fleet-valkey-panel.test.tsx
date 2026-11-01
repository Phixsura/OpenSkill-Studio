import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetValkeyPanel } from "@/components/fleet-valkey-panel";
describe("FleetValkeyPanel", () => { it("renders", () => {
    const { container } = render(<FleetValkeyPanel nodes={6} online={6} keys={60000000} memoryGb={192} />);
    expect(container.textContent).toContain("Valkey");
}); });

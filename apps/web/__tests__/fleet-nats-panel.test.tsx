import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNatsPanel } from "@/components/fleet-nats-panel";
describe("FleetNatsPanel", () => { it("renders", () => {
    const { container } = render(<FleetNatsPanel servers={3} connected={3} subscriptions={3000} msgsPerSec={150000} />);
    expect(container.textContent).toContain("NATS");
    expect(container.textContent).toContain("150,000 msg/s");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBullmqPanel } from "@/components/fleet-bullmq-panel";
describe("FleetBullmqPanel", () => { it("renders", () => {
    const { container } = render(<FleetBullmqPanel queues={10} waiting={100} active={20} completed={50000} failed={0} />);
    expect(container.textContent).toContain("BullMQ");
    expect(container.textContent).toContain("50,000");
}); });

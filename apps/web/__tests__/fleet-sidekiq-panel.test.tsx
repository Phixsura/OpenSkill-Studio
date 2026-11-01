import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSidekiqPanel } from "@/components/fleet-sidekiq-panel";
describe("FleetSidekiqPanel", () => { it("renders", () => {
    const { container } = render(<FleetSidekiqPanel processes={10} busy={50} enqueued={200} dead={5} />);
    expect(container.textContent).toContain("Sidekiq");
    expect(container.textContent).toContain("5 dead");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTriggerdevPanel } from "@/components/fleet-triggerdev-panel";
describe("FleetTriggerdevPanel", () => { it("renders", () => {
    const { container } = render(<FleetTriggerdevPanel projects={5} active={5} runs={250000} tasks={200} />);
    expect(container.textContent).toContain("Trigger.dev");
}); });

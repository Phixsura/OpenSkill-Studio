import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWandbPanel } from "@/components/fleet-wandb-panel";
describe("FleetWandbPanel", () => { it("renders", () => {
    const { container } = render(<FleetWandbPanel projects={10} active={10} runs={10000} artifacts={2000} />);
    expect(container.textContent).toContain("W&B");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReplicatePanel } from "@/components/fleet-replicate-panel";
describe("FleetReplicatePanel", () => { it("renders", () => {
    const { container } = render(<FleetReplicatePanel models={20} active={20} predictions={2000000} avgRunSec={3} />);
    expect(container.textContent).toContain("Replicate");
}); });

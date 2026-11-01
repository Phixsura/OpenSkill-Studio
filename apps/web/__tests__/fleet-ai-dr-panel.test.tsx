import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDrPanel } from "@/components/fleet-ai-dr-panel";
describe("FleetAiDrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDrPanel plans={3} active={3} rto={10} rpo={3} lastDrill={5} />);
    expect(container.textContent).toContain("Disaster Recovery");
}); });

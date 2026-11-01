import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAccessCtlPanel } from "@/components/fleet-ai-access-ctl-panel";
describe("FleetAiAccessCtlPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAccessCtlPanel controllers={4} active={4} policies={500} evaluations={200000000} denied={5000} />);
    expect(container.textContent).toContain("Access Control");
}); });

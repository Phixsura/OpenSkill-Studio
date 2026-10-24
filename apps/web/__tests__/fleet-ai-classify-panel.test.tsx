import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiClassifyPanel } from "@/components/fleet-ai-classify-panel";
describe("FleetAiClassifyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiClassifyPanel services={5} active={5} classifications={25000000} accuracy={98} />);
    expect(container.textContent).toContain("AI Classification");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDxV8Panel } from "@/components/fleet-ai-dx-v8-panel";
describe("FleetAiDxV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDxV8Panel trackers={3} active={3} nps={90} ttfv={1} satisfaction={99} />);
    expect(container.textContent).toContain("AI DX v8");
}); });

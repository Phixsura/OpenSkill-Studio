import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFinopsV8Panel } from "@/components/fleet-ai-finops-v8-panel";
describe("FleetAiFinopsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiFinopsV8Panel trackers={3} active={3} spend={200000000} savings={80000000} unitCost={0.0000003} />);
    expect(container.textContent).toContain("FinOps v8");
}); });

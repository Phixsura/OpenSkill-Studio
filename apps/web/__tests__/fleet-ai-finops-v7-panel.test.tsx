import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFinopsV7Panel } from "@/components/fleet-ai-finops-v7-panel";
describe("FleetAiFinopsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiFinopsV7Panel trackers={3} active={3} spend={50000000} savings={20000000} costPerReq={0.000005} roi={40} />);
    expect(container.textContent).toContain("FinOps v7");
}); });

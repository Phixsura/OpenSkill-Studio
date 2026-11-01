import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFinopsV6Panel } from "@/components/fleet-ai-finops-v6-panel";
describe("FleetAiFinopsV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiFinopsV6Panel trackers={3} active={3} spend={20000000} savings={8000000} costPerReq={0.000005} />);
    expect(container.textContent).toContain("FinOps v6");
}); });

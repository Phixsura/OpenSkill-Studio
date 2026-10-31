import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNetPolicyPanel } from "@/components/fleet-ai-net-policy-panel";
describe("FleetAiNetPolicyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNetPolicyPanel policies={5} active={5} rules={200} blocked={10000} allowed={200000000} />);
    expect(container.textContent).toContain("Network Policy");
}); });

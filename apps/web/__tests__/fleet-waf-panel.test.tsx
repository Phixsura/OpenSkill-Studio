import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWafPanel } from "@/components/fleet-waf-panel";
describe("FleetWafPanel", () => { it("renders", () => {
    const { container } = render(<FleetWafPanel rules={25} blocked={700} allowed={14300} blockRate={4.67} />);
    expect(container.textContent).toContain("WAF");
    expect(container.textContent).toContain("700 blocked");
}); });

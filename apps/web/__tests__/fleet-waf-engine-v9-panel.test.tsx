import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWafEngineV9Panel } from "@/components/fleet-waf-engine-v9-panel";
describe("FleetWafEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWafEngineV9Panel rules={200} blocked={5000} />);
    expect(container.textContent).toContain("WAF Engine v9");
}); });

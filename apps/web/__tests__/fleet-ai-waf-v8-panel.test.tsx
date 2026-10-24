import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWafV8Panel } from "@/components/fleet-ai-waf-v8-panel";
describe("FleetAiWafV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiWafV8Panel wafs={5} active={5} rules={10000} blocked={20000000} mlRules={1000} />);
    expect(container.textContent).toContain("WAF v8");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWafV4Panel } from "@/components/fleet-ai-waf-v4-panel";
describe("FleetAiWafV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiWafV4Panel wafs={5} active={5} rules={2000} blocked={2000000} mlRules={500} />);
    expect(container.textContent).toContain("AI WAF v4");
}); });

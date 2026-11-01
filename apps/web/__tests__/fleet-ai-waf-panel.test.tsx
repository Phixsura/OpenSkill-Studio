import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWafPanel } from "@/components/fleet-ai-waf-panel";
describe("FleetAiWafPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWafPanel wafs={5} active={5} requests={500000000} blocked={200000} rules={500} />);
    expect(container.textContent).toContain("AI WAF");
}); });

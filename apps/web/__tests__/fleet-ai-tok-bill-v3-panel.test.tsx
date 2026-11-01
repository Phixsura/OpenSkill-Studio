import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokBillV3Panel } from "@/components/fleet-ai-tok-bill-v3-panel";
describe("FleetAiTokBillV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokBillV3Panel meters={5} active={5} tokens={500000000000} revenue={2000000} customers={50000} />);
    expect(container.textContent).toContain("Token Billing v3");
}); });

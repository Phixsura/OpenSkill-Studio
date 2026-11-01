import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelBillV2Panel } from "@/components/fleet-ai-model-bill-v2-panel";
describe("FleetAiModelBillV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelBillV2Panel billers={3} active={3} models={500} revenue={1000000} invoices={20000} />);
    expect(container.textContent).toContain("Model Billing v2");
}); });

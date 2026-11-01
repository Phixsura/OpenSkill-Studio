import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUnitEconomicsV8Panel } from "@/components/fleet-ai-unit-economics-v8-panel";
describe("FleetAiUnitEconomicsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiUnitEconomicsV8Panel trackers={3} active={3} ltv={200000} cac={15000} ltvCac={13.3} payback={4} />);
    expect(container.textContent).toContain("Unit Economics v8");
}); });

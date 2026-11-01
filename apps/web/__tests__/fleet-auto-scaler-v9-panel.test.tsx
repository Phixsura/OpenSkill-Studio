import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAutoScalerV9Panel } from "@/components/fleet-auto-scaler-v9-panel";
describe("FleetAutoScalerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAutoScalerV9Panel targets={20} replicas={80} />);
    expect(container.textContent).toContain("Auto Scaler v9");
}); });

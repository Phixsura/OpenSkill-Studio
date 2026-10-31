import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiQualityGateV9Panel } from "@/components/fleet-api-quality-gate-v9-panel";
describe("FleetApiQualityGateV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiQualityGateV9Panel gates={20} blocked={0} />);
    expect(container.textContent).toContain("Quality Gate v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataQualityPanel } from "@/components/fleet-data-quality-panel";
describe("FleetDataQualityPanel", () => { it("renders", () => {
    const { container } = render(<FleetDataQualityPanel total={50} good={40} poor={3} avgScore={88} highQuality={false} />);
    expect(container.textContent).toContain("Data Quality");
    expect(container.textContent).toContain("88/100");
}); });

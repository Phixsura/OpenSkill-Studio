import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDataQualityV9Panel } from "@/components/fleet-api-data-quality-v9-panel";
describe("FleetApiDataQualityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDataQualityV9Panel apis={100} score={99} />);
    expect(container.textContent).toContain("Data Quality v9");
}); });

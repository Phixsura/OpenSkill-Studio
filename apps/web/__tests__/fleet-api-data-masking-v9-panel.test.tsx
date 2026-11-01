import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDataMaskingV9Panel } from "@/components/fleet-api-data-masking-v9-panel";
describe("FleetApiDataMaskingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDataMaskingV9Panel endpoints={100} piiFields={500} />);
    expect(container.textContent).toContain("Data Masking v9");
}); });

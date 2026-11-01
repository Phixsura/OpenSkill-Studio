import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMaturityModelV9Panel } from "@/components/fleet-api-maturity-model-v9-panel";
describe("FleetApiMaturityModelV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMaturityModelV9Panel apis={100} avgLevel={4.2} />);
    expect(container.textContent).toContain("API Maturity v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDataValidationV9Panel } from "@/components/fleet-api-data-validation-v9-panel";
describe("FleetApiDataValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDataValidationV9Panel validators={50} anomalies={0} />);
    expect(container.textContent).toContain("Data Validation v9");
}); });

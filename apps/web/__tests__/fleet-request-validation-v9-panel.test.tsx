import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRequestValidationV9Panel } from "@/components/fleet-request-validation-v9-panel";
describe("FleetRequestValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRequestValidationV9Panel validators={50} rejected={50} />);
    expect(container.textContent).toContain("Request Validation v9");
}); });

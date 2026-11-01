import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiFieldValidationV9Panel } from "@/components/fleet-api-field-validation-v9-panel";
describe("FleetApiFieldValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiFieldValidationV9Panel rules={200} fields={500000} />);
    expect(container.textContent).toContain("Field Validation v9");
}); });

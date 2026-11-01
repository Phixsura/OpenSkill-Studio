import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiInputValidationV9Panel } from "@/components/fleet-api-input-validation-v9-panel";
describe("FleetApiInputValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiInputValidationV9Panel endpoints={200} rejected={100} />);
    expect(container.textContent).toContain("Input Validation v9");
}); });

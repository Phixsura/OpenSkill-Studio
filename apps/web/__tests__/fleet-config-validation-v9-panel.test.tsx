import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigValidationV9Panel } from "@/components/fleet-config-validation-v9-panel";
describe("FleetConfigValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetConfigValidationV9Panel configs={100} invalid={0} />);
    expect(container.textContent).toContain("Config Validation v9");
}); });

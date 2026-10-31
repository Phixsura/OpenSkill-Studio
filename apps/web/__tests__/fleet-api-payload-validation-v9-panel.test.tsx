import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPayloadValidationV9Panel } from "@/components/fleet-api-payload-validation-v9-panel";
describe("FleetApiPayloadValidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPayloadValidationV9Panel validators={50} rejected={50} />);
    expect(container.textContent).toContain("Payload Validation v9");
}); });

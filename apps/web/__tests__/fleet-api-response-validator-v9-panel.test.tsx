import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiResponseValidatorV9Panel } from "@/components/fleet-api-response-validator-v9-panel";
describe("FleetApiResponseValidatorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiResponseValidatorV9Panel validators={50} violations={0} />);
    expect(container.textContent).toContain("Response Validator v9");
}); });

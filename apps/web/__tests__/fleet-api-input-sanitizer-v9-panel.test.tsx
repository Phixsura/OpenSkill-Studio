import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiInputSanitizerV9Panel } from "@/components/fleet-api-input-sanitizer-v9-panel";
describe("FleetApiInputSanitizerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiInputSanitizerV9Panel endpoints={200} blocked={60} />);
    expect(container.textContent).toContain("Input Sanitizer v9");
}); });

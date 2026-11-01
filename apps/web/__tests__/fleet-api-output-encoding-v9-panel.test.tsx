import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiOutputEncodingV9Panel } from "@/components/fleet-api-output-encoding-v9-panel";
describe("FleetApiOutputEncodingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiOutputEncodingV9Panel endpoints={200} encoded={200} />);
    expect(container.textContent).toContain("Output Encoding v9");
}); });

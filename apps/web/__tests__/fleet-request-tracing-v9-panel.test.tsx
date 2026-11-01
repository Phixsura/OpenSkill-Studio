import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRequestTracingV9Panel } from "@/components/fleet-request-tracing-v9-panel";
describe("FleetRequestTracingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRequestTracingV9Panel traces={10000} errors={0} />);
    expect(container.textContent).toContain("Request Tracing v9");
}); });

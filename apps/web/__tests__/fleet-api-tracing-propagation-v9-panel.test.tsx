import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTracingPropagationV9Panel } from "@/components/fleet-api-tracing-propagation-v9-panel";
describe("FleetApiTracingPropagationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTracingPropagationV9Panel services={200} propagating={200} />);
    expect(container.textContent).toContain("Trace Propagation v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDistributedTracingV9Panel } from "@/components/fleet-distributed-tracing-v9-panel";
describe("FleetDistributedTracingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDistributedTracingV9Panel services={200} sps={100000} />);
    expect(container.textContent).toContain("Distributed Tracing v9");
}); });

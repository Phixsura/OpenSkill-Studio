import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPerfV5Panel } from "@/components/fleet-ai-perf-v5-panel";
describe("FleetAiPerfV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPerfV5Panel monitors={5} active={5} p50={5} p99={30} rps={50000000} />);
    expect(container.textContent).toContain("Performance v5");
}); });

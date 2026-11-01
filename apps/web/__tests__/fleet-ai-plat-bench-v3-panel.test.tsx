import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatBenchV3Panel } from "@/components/fleet-ai-plat-bench-v3-panel";
describe("FleetAiPlatBenchV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatBenchV3Panel benches={5} active={5} tests={5000} p99={30} throughput={20000000} />);
    expect(container.textContent).toContain("Platform Benchmark v3");
}); });

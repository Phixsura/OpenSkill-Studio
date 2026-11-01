import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiComputeAllocV2Panel } from "@/components/fleet-ai-compute-alloc-v2-panel";
describe("FleetAiComputeAllocV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiComputeAllocV2Panel allocators={5} active={5} gpus={10000} allocated={9000} efficiency={90} costSaved={35} />);
    expect(container.textContent).toContain("Compute Allocator v2");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiResAllocPanel } from "@/components/fleet-ai-res-alloc-panel";
describe("FleetAiResAllocPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiResAllocPanel allocators={5} active={5} gpus={5000} allocated={4750} waste={5} />);
    expect(container.textContent).toContain("Resource Allocator");
}); });

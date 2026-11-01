import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiKvCachePanel } from "@/components/fleet-ai-kv-cache-panel";
describe("FleetAiKvCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiKvCachePanel caches={8} active={8} sizeGb={1024} hitRate={95} evictions={10000} />);
    expect(container.textContent).toContain("KV Cache");
}); });

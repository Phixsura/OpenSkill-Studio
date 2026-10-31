import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiShardPanel } from "@/components/fleet-ai-shard-panel";
describe("FleetAiShardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiShardPanel configs={3} active={3} shards={128} models={20} rebalances={5} />);
    expect(container.textContent).toContain("Model Sharding");
}); });

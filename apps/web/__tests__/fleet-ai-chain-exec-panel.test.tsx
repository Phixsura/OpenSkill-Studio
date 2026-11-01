import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChainExecPanel } from "@/components/fleet-ai-chain-exec-panel";
describe("FleetAiChainExecPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChainExecPanel executors={4} active={4} chains={2000000} steps={20000000} latency={150} />);
    expect(container.textContent).toContain("Chain Executor");
}); });

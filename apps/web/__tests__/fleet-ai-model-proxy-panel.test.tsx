import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelProxyPanel } from "@/components/fleet-ai-model-proxy-panel";
describe("FleetAiModelProxyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelProxyPanel proxies={5} active={5} requests={500000000} models={50} overhead={1.5} />);
    expect(container.textContent).toContain("Model Proxy");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVllmPanel } from "@/components/fleet-vllm-panel";
describe("FleetVllmPanel", () => { it("renders", () => {
    const { container } = render(<FleetVllmPanel instances={5} running={5} tokensPerSec={25000} gpus={40} />);
    expect(container.textContent).toContain("vLLM");
}); });

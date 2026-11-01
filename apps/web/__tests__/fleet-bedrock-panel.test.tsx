import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBedrockPanel } from "@/components/fleet-bedrock-panel";
describe("FleetBedrockPanel", () => { it("renders", () => {
    const { container } = render(<FleetBedrockPanel models={10} available={10} invocations={5000000} tokens={2000000000} />);
    expect(container.textContent).toContain("Bedrock");
}); });

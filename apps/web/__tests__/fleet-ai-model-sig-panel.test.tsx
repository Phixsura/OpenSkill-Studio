import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelSigPanel } from "@/components/fleet-ai-model-sig-panel";
describe("FleetAiModelSigPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelSigPanel validators={4} active={4} models={500} schemas={1000} violations={0} />);
    expect(container.textContent).toContain("Model Signature");
}); });

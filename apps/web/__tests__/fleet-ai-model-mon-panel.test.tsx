import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelMonPanel } from "@/components/fleet-ai-model-mon-panel";
describe("FleetAiModelMonPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelMonPanel monitors={5} active={5} models={200} alerts={10} degraded={0} />);
    expect(container.textContent).toContain("Model Monitor");
}); });

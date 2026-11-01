import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCompressPanel } from "@/components/fleet-ai-compress-panel";
describe("FleetAiCompressPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCompressPanel pipelines={4} active={4} models={50} reduction={70} qualityLoss={0.8} />);
    expect(container.textContent).toContain("Model Compression");
}); });

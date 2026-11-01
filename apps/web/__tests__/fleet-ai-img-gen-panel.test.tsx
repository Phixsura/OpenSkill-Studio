import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiImgGenPanel } from "@/components/fleet-ai-img-gen-panel";
describe("FleetAiImgGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiImgGenPanel generators={4} active={4} images={10000000} latency={2.5} resolutions={["1024x1024", "2048x2048"]} />);
    expect(container.textContent).toContain("Image Generation");
}); });

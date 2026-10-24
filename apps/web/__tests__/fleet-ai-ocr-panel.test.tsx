import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOcrPanel } from "@/components/fleet-ai-ocr-panel";
describe("FleetAiOcrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOcrPanel services={5} active={5} pages={5000000} accuracy={99} />);
    expect(container.textContent).toContain("AI OCR");
}); });

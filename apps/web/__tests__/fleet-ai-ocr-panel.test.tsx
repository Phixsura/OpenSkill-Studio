import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOcrPanel } from "@/components/fleet-ai-ocr-panel";
describe("FleetAiOcrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOcrPanel engines={4} active={4} pages={20000000} accuracy={99.5} languages={80} />);
    expect(container.textContent).toContain("AI OCR");
}); });

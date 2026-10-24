import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelAnnotPanel } from "@/components/fleet-ai-model-annot-panel";
describe("FleetAiModelAnnotPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelAnnotPanel annotators={3} active={3} models={1000} annotations={10000} tags={5000} />);
    expect(container.textContent).toContain("Model Annotation");
}); });

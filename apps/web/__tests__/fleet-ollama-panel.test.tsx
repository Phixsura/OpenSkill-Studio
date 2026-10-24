import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOllamaPanel } from "@/components/fleet-ollama-panel";
describe("FleetOllamaPanel", () => { it("renders", () => {
    const { container } = render(<FleetOllamaPanel instances={10} running={10} modelsLoaded={20} requests={500000} />);
    expect(container.textContent).toContain("Ollama");
}); });

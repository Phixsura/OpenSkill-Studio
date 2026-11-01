import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelAlogPanel } from "@/components/fleet-ai-model-alog-panel";
describe("FleetAiModelAlogPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelAlogPanel loggers={3} active={3} accesses={5000000} users={20000} models={500} />);
    expect(container.textContent).toContain("Model Access Log");
}); });

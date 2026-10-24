import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEarlyStopPanel } from "@/components/fleet-ai-early-stop-panel";
describe("FleetAiEarlyStopPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEarlyStopPanel managers={3} active={3} jobs={200} stopped={60} saved={30} />);
    expect(container.textContent).toContain("Early Stopping");
}); });

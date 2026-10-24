import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNsMgrPanel } from "@/components/fleet-ai-ns-mgr-panel";
describe("FleetAiNsMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNsMgrPanel managers={3} active={3} namespaces={200} resources={10000} conflicts={0} />);
    expect(container.textContent).toContain("Namespace Manager");
}); });

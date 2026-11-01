import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSdkGenPanel } from "@/components/fleet-ai-sdk-gen-panel";
describe("FleetAiSdkGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSdkGenPanel generators={2} active={2} sdks={100} languages={10} downloads={500000} />);
    expect(container.textContent).toContain("SDK Generator");
}); });

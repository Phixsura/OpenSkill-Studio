import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPinjectionPanel } from "@/components/fleet-ai-pinjection-panel";
describe("FleetAiPinjectionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPinjectionPanel services={5} active={5} scanned={50000000} blocked={25000} blockRate={0.05} />);
    expect(container.textContent).toContain("Prompt Injection");
}); });

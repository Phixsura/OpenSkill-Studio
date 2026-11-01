import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDevsecopsV7Panel } from "@/components/fleet-ai-devsecops-v7-panel";
describe("FleetAiDevsecopsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDevsecopsV7Panel systems={4} active={4} scans={50000} vulns={100} fixed={100} sast={100} />);
    expect(container.textContent).toContain("DevSecOps v7");
}); });

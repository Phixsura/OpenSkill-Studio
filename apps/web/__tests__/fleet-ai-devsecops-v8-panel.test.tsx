import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDevsecopsV8Panel } from "@/components/fleet-ai-devsecops-v8-panel";
describe("FleetAiDevsecopsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDevsecopsV8Panel systems={5} active={5} scans={200000} vulns={200} fixed={200} sast={100} />);
    expect(container.textContent).toContain("DevSecOps v8");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetExtSecretsPanel } from "@/components/fleet-ext-secrets-panel";
describe("FleetExtSecretsPanel", () => { it("renders", () => {
    const { container } = render(<FleetExtSecretsPanel total={30} synced={28} failed={2} healthy={false} />);
    expect(container.textContent).toContain("External Secrets");
    expect(container.textContent).toContain("2 sync errors");
}); });

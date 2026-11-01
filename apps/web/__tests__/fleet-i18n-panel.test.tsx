import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetI18nPanel } from "@/components/fleet-i18n-panel";
describe("FleetI18nPanel", () => { it("renders", () => {
    const { container } = render(<FleetI18nPanel totalStrings={1000} translated={800} coveragePct={80} languages={5} ready={false} />);
    expect(container.textContent).toContain("i18n Coverage");
    expect(container.textContent).toContain("Not localization-ready");
}); });

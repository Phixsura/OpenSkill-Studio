import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSymphony } from "@/components/platform-symphony";
describe("PlatformSymphony", () => { it("renders", () => {
    const { container } = render(<PlatformSymphony />);
    expect(container.textContent).toContain("SYMPHONY");
    expect(container.textContent).toContain("Allegro");
    expect(container.textContent).toContain("Finale");
}); });

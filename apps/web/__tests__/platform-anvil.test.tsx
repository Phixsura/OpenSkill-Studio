import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAnvil } from "@/components/platform-anvil";
describe("PlatformAnvil", () => { it("renders", () => {
    const { container } = render(<PlatformAnvil />);
    expect(container.textContent).toContain("ANVIL");
    expect(container.textContent).toContain("PRISTINE");
}); });

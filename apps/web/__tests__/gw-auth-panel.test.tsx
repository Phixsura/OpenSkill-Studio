import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwAuthPanel } from "@/components/gw-auth-panel";
describe("GwAuthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwAuthPanel totalAuth={10000} denied={500} keysRegistered={50} />
    );
    expect(container.textContent).toContain("Gateway Auth");
    expect(container.textContent).toContain("50 keys");
    expect(container.textContent).toContain("5% deny rate");
    expect(container.textContent).toContain("9,500");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("10,000");
  });
});

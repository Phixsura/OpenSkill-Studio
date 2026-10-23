import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfoTooltip } from "@/components/info-tooltip";

describe("InfoTooltip", () => {
  it("renders trigger", () => {
    const { container } = render(
      <InfoTooltip title="API Key" content="Your secret key" link="/docs/auth" />
    );
    expect(container.textContent).toContain("?");
  });
  it("shows tooltip on hover", () => {
    const { container } = render(
      <InfoTooltip title="API Key" content="Your secret key" link="/docs/auth" />
    );
    fireEvent.mouseEnter(container.querySelector("button")!);
    expect(container.textContent).toContain("API Key");
    expect(container.textContent).toContain("Your secret key");
    expect(container.textContent).toContain("Learn more");
  });
});

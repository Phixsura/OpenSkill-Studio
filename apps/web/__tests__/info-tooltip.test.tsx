import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfoTooltip } from "@/components/info-tooltip";

describe("InfoTooltip", () => {
  it("shows on hover", () => {
    const { container, getByText } = render(
      <InfoTooltip title="API Key" body="Keep it secret">
        <span>ℹ️</span>
      </InfoTooltip>
    );
    expect(container.textContent).toContain("ℹ️");
    expect(container.textContent).not.toContain("Keep it secret");
    fireEvent.mouseEnter(getByText("ℹ️"));
    expect(container.textContent).toContain("API Key");
    expect(container.textContent).toContain("Keep it secret");
  });
});

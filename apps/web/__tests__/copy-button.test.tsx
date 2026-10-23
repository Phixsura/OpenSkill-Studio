import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CopyButton } from "@/components/copy-button";

describe("CopyButton", () => {
  it("renders with label", () => {
    const { container } = render(
      <CopyButton value="sk_live_abc" display="sk_l••••_abc" label="API Key" sensitive={true} />
    );
    expect(container.textContent).toContain("API Key");
    expect(container.textContent).toContain("sk_l••••_abc");
    expect(container.textContent).toContain("Copy");
  });

  it("reveals on click", () => {
    const { container, getByText } = render(
      <CopyButton value="secret123" display="••••••••" label="" sensitive={true} />
    );
    expect(container.textContent).toContain("••••••••");
    fireEvent.click(getByText("👁️"));
    expect(container.textContent).toContain("secret123");
  });
});

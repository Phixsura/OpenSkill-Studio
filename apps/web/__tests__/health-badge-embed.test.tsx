import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HealthBadgeEmbed } from "@/components/health-badge-embed";

describe("HealthBadgeEmbed", () => {
  it("renders", () => {
    const { container } = render(
      <HealthBadgeEmbed badgeUrl="https://img.shields.io/badge/x" markdown="![Status](url)"
        htmlCode='<img src="url">' status="healthy" uptimePct={99.99} onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Health Badge");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("![Status](url)");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <HealthBadgeEmbed badgeUrl="x" markdown="md" htmlCode="ht" status="healthy"
        uptimePct={100} onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith("md");
  });
});

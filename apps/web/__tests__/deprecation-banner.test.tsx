import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeprecationBanner } from "@/components/deprecation-banner";

describe("DeprecationBanner", () => {
  it("shows version", () => {
    const { container } = render(<DeprecationBanner version="1.0.0" sunsetDate="2026-12-01" daysRemaining={60} />);
    expect(container.textContent).toContain("1.0.0");
  });

  it("shows days remaining", () => {
    const { container } = render(<DeprecationBanner version="1.0.0" sunsetDate="2026-12-01" daysRemaining={30} />);
    expect(container.textContent).toContain("30 days");
  });

  it("shows replacement version", () => {
    const { container } = render(<DeprecationBanner version="1.0.0" sunsetDate="2026-12-01" daysRemaining={60} replacementVersion="2.0.0" />);
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows migration link", () => {
    const { container } = render(<DeprecationBanner version="1.0.0" sunsetDate="2026-12-01" daysRemaining={60} migrationGuideUrl="https://docs.example.com" />);
    expect(container.querySelector("a")?.href).toContain("docs.example.com");
  });

  it("shows urgent styling for <=7 days", () => {
    const { container } = render(<DeprecationBanner version="1.0.0" sunsetDate="2026-12-01" daysRemaining={3} />);
    expect(container.textContent).toContain("🚨");
  });
});

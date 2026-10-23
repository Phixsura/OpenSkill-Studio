import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CertificationCard } from "@/components/certification-card";

describe("CertificationCard", () => {
  it("renders cert", () => {
    const onStart = vi.fn();
    const { container, getByText } = render(
      <CertificationCard id="platform_basics" title="Platform Basics" icon="📘"
        modules={5} passingScore={80} userScore={null} completed={false} onStart={onStart} />
    );
    expect(container.textContent).toContain("Platform Basics");
    expect(container.textContent).toContain("5 modules");
    expect(container.textContent).toContain("80% to pass");
    fireEvent.click(getByText("Start"));
    expect(onStart).toHaveBeenCalled();
  });

  it("renders completed", () => {
    const { container } = render(
      <CertificationCard id="x" title="API Expert" icon="🔧"
        modules={8} passingScore={85} userScore={92} completed={true} onStart={vi.fn()} />
    );
    expect(container.textContent).toContain("Certified");
    expect(container.textContent).toContain("92%");
  });
});

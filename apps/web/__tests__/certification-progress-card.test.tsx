import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CertificationProgressCard } from "@/components/certification-progress-card";

describe("CertificationProgressCard", () => {
  const certs = [
    { id: "basics", label: "Basics", icon: "🎓", required_score: 80, completed: true },
    { id: "api", label: "API Expert", icon: "🔌", required_score: 85, completed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <CertificationProgressCard certifications={certs} completed={1} total={2}
        progressPct={50} onTakeExam={vi.fn()} />
    );
    expect(container.textContent).toContain("Certifications");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("✅ Certified");
    expect(container.textContent).toContain("Take Exam");
  });
  it("take exam", () => {
    const fn = vi.fn();
    const { container } = render(
      <CertificationProgressCard certifications={certs} completed={1} total={2}
        progressPct={50} onTakeExam={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Take Exam")!);
    expect(fn).toHaveBeenCalledWith("api");
  });
});

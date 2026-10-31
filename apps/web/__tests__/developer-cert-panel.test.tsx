import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperCertPanel } from "@/components/developer-cert-panel";

const certs = [
  { certId: "sdk-101", name: "SDK Fundamentals", description: "Core skills", passingScore: 70, questions: 50 },
  { certId: "adv-201", name: "Advanced SDK", description: "Advanced topics", passingScore: 80, questions: 40 },
];
const results = [
  { certId: "sdk-101", score: 92, passed: true, certificateCode: "CERT-ABC123", expiresAt: "2025-12-31" },
];

describe("DeveloperCertPanel", () => {
  it("renders certs with status", () => {
    const { container } = render(<DeveloperCertPanel certs={certs} results={results} />);
    expect(container.textContent).toContain("SDK Fundamentals");
    expect(container.textContent).toContain("Certified");
    expect(container.textContent).toContain("CERT-ABC123");
  });
  it("shows Take Exam for uncertified", () => {
    const fn = vi.fn();
    const { getByText } = render(<DeveloperCertPanel certs={certs} results={results} onTakeExam={fn} />);
    fireEvent.click(getByText("Take Exam"));
    expect(fn).toHaveBeenCalledWith("adv-201");
  });
});

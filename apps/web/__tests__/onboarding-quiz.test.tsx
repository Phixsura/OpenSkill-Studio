import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingQuiz } from "@/components/onboarding-quiz";

describe("OnboardingQuiz", () => {
  const questions = [
    { id: "q1", text: "How familiar?", options: ["Beginner", "Expert"] },
    { id: "q2", text: "Goal?", options: ["Build", "Publish"] },
  ];
  it("shows first question", () => {
    const { container } = render(<OnboardingQuiz questions={questions} onComplete={vi.fn()} />);
    expect(container.textContent).toContain("How familiar?");
    expect(container.textContent).toContain("1 of 2");
  });
  it("advances on select", () => {
    const { container } = render(<OnboardingQuiz questions={questions} onComplete={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Expert")!);
    expect(container.textContent).toContain("Goal?");
  });
  it("completes on last", () => {
    const fn = vi.fn();
    const oneQ = [{ id: "q1", text: "Q?", options: ["A", "B"] }];
    const { container } = render(<OnboardingQuiz questions={oneQ} onComplete={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith({ q1: "A" });
  });
});

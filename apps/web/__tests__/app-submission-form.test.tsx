import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSubmissionForm } from "@/components/app-submission-form";

describe("AppSubmissionForm", () => {
  it("renders form", () => {
    const onSubmit = vi.fn();
    const { container, getByText } = render(
      <AppSubmissionForm onSubmit={onSubmit} submitting={false}
        errors={[{ field: "name", error: "Name is required" }]} />
    );
    expect(container.textContent).toContain("Submit App");
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("Name is required");
    fireEvent.click(getByText("Submit for Review"));
    expect(onSubmit).toHaveBeenCalled();
  });
});

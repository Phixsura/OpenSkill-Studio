import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DevAgreementChecklist } from "@/components/dev-agreement-checklist";

describe("DevAgreementChecklist", () => {
  it("renders agreements", () => {
    const onAccept = vi.fn();
    const { container, getByText } = render(
      <DevAgreementChecklist allAccepted={false} onAccept={onAccept}
        agreements={[
          { id: "tos", title: "TOS", version: "2.0", required: true, accepted: true, outdated: false },
          { id: "dpa", title: "DPA", version: "1.0", required: true, accepted: false, outdated: false },
        ]} />
    );
    expect(container.textContent).toContain("Developer Agreements");
    expect(container.textContent).toContain("Action required");
    expect(container.textContent).toContain("TOS");
    expect(container.textContent).toContain("DPA");
    expect(container.textContent).toContain("Required");
    fireEvent.click(getByText("Accept"));
    expect(onAccept).toHaveBeenCalledWith("dpa");
  });
});

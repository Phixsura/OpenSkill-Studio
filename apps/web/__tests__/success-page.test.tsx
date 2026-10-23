import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SuccessPage } from "@/components/success-page";

describe("SuccessPage", () => {
  it("renders success", () => {
    const onDone = vi.fn();
    const { container, getByText } = render(
      <SuccessPage title="App Installed! 🎉" body="Slack Bot installed"
        next={["Configure webhooks", "View docs"]} showConfetti={true}
        onNext={vi.fn()} onDone={onDone} />
    );
    expect(container.textContent).toContain("App Installed!");
    expect(container.textContent).toContain("Slack Bot installed");
    expect(container.textContent).toContain("Configure webhooks");
    expect(container.textContent).toContain("What's next?");
    fireEvent.click(getByText("Done"));
    expect(onDone).toHaveBeenCalled();
  });
});

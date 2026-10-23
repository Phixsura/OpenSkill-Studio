import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotFoundPage } from "@/components/not-found-page";

describe("NotFoundPage", () => {
  it("renders", () => {
    const { container } = render(
      <NotFoundPage title="App Not Found" message="The app doesn't exist" icon="🔍"
        suggestions={["Check the URL"]} actions={[{ label: "Go Home", url: "/", primary: true }]} />
    );
    expect(container.textContent).toContain("App Not Found");
    expect(container.textContent).toContain("Check the URL");
    expect(container.textContent).toContain("Go Home");
    expect(container.textContent).toContain("🔍");
  });
});

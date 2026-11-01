from app.services.app_api_developer_getting_started import AppAPIDeveloperGettingStarted

class TestGettingStarted:
    def test_add(self):
        g = AppAPIDeveloperGettingStarted()
        s = g.add_section("inst-1", "s1", "Install", "npm install @sdk/client", "npm install @sdk/client", "bash", 1)
        assert s.language == "bash"

    def test_ordered(self):
        g = AppAPIDeveloperGettingStarted()
        g.add_section("inst-1", "s2", "Auth", "Setup auth", order=2)
        g.add_section("inst-1", "s1", "Install", "Install SDK", order=1)
        sections = g.list_sections("inst-1")
        assert sections[0].section_id == "s1"

    def test_isolation(self):
        g = AppAPIDeveloperGettingStarted()
        g.add_section("inst-1", "s1", "Install", "Content")
        assert g.list_sections("inst-2") == []

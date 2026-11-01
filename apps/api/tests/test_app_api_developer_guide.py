from app.services.app_api_developer_guide import AppAPIDeveloperGuide

class TestGuide:
    def test_create(self):
        g = AppAPIDeveloperGuide()
        guide = g.create("inst-1", "g1", "Getting Started", "quickstart", [{"step_id": "s1", "title": "Install SDK", "content": "npm install"}])
        assert len(guide.steps) == 1

    def test_view(self):
        g = AppAPIDeveloperGuide()
        g.create("inst-1", "g1", "Guide", "cat", [{"step_id": "s1", "title": "Step"}])
        g.record_view("inst-1", "g1")
        assert g.list_guides("inst-1")[0].view_count == 1

    def test_by_category(self):
        g = AppAPIDeveloperGuide()
        g.create("inst-1", "g1", "A", "auth", [{"step_id": "s1", "title": "S"}])
        g.create("inst-1", "g2", "B", "webhooks", [{"step_id": "s1", "title": "S"}])
        assert len(g.by_category("inst-1", "auth")) == 1

    def test_isolation(self):
        g = AppAPIDeveloperGuide()
        g.create("inst-1", "g1", "A", "cat", [{"step_id": "s1", "title": "S"}])
        assert g.list_guides("inst-2") == []

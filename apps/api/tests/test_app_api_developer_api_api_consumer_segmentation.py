from app.services.app_api_developer_api_api_consumer_segmentation import AppAPIDeveloperAPIApiConsumerSegmentation

class TestConsumerSegmentation:
    def test_create(self):
        s = AppAPIDeveloperAPIApiConsumerSegmentation()
        seg = s.create_segment("inst-1", "s1", "Power Users", {"min_calls": "1000"})
        assert seg.name == "Power Users"

    def test_membership(self):
        s = AppAPIDeveloperAPIApiConsumerSegmentation()
        s.create_segment("inst-1", "s1", "VIP")
        s.add_member("inst-1", "s1", "c1")
        assert s.is_member("inst-1", "s1", "c1") is True
        assert s.is_member("inst-1", "s1", "c2") is False

    def test_remove(self):
        s = AppAPIDeveloperAPIApiConsumerSegmentation()
        s.create_segment("inst-1", "s1", "VIP")
        s.add_member("inst-1", "s1", "c1")
        s.remove_member("inst-1", "s1", "c1")
        assert s.is_member("inst-1", "s1", "c1") is False

    def test_consumer_segments(self):
        s = AppAPIDeveloperAPIApiConsumerSegmentation()
        s.create_segment("inst-1", "s1", "VIP")
        s.create_segment("inst-1", "s2", "Enterprise")
        s.add_member("inst-1", "s1", "c1")
        s.add_member("inst-1", "s2", "c1")
        assert len(s.consumer_segments("inst-1", "c1")) == 2

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiConsumerSegmentation()
        s.create_segment("inst-1", "s1", "VIP")
        assert len(s.list_segments("inst-2")) == 0

from app.services.pipeline.host_config import host_matches_rule, url_host_in_csv


def test_url_host_in_csv_exact_match() -> None:
    assert url_host_in_csv("https://example.com/a", "example.com") is True
    assert url_host_in_csv("https://www.example.com/a", "example.com") is True


def test_url_host_in_csv_wildcard_subdomain() -> None:
    assert url_host_in_csv("https://app.client.io/path", "*.client.io") is True
    assert url_host_in_csv("https://client.io/", "*.client.io") is True
    assert url_host_in_csv("https://other.net/", "*.client.io") is False


def test_url_host_in_csv_multiple() -> None:
    assert url_host_in_csv("https://b.com/x", "a.com, b.com, c.com") is True
    assert url_host_in_csv("https://z.com/", "a.com, b.com") is False


def test_host_matches_rule() -> None:
    assert host_matches_rule("app.foo.dev", "*.foo.dev") is True
    assert host_matches_rule("foo.dev", "*.foo.dev") is True
    assert host_matches_rule("foo.dev", "foo.dev") is True
    assert host_matches_rule("evilfoo.dev", "*.foo.dev") is False

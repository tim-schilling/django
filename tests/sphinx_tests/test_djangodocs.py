from types import SimpleNamespace

from sphinx_tests.tests import SimpleSphinxTestCase

# The import must happen at the end of setUpClass, so it can't be imported at
# the top of the file.
djangodocs = None


class DjangoDocsTests(SimpleSphinxTestCase):
    @classmethod
    def docs_module_import(cls):
        """Override this method to allow importing code in the docs folder."""
        # Linters/IDEs may not be able to detect this as a valid import.
        import djangodocs as _djangodocs

        global djangodocs
        djangodocs = _djangodocs

    def sourcefile(self, text, *, version="6.2", next_version="6.2"):
        config = SimpleNamespace(
            version=version,
            django_next_version=next_version,
        )
        env = SimpleNamespace(config=config)
        settings = SimpleNamespace(env=env)
        document = SimpleNamespace(settings=settings)
        inliner = SimpleNamespace(document=document)
        return djangodocs.sourcefile("sourcefile", "", text, 1, inliner)

    def test_sourcefile_uses_main_branch(self):
        role_nodes, messages = self.sourcefile("django/forms/forms.py")

        self.assertEqual(messages, [])
        self.assertEqual(role_nodes[0].astext(), "django/forms/forms.py")
        self.assertEqual(
            role_nodes[0]["refuri"],
            "https://github.com/django/django/blob/main/django/forms/forms.py",
        )

    def test_sourcefile_uses_stable_branch(self):
        role_nodes, messages = self.sourcefile(
            "django/forms/forms.py", version="6.0", next_version="6.2"
        )

        self.assertEqual(messages, [])
        self.assertEqual(
            role_nodes[0]["refuri"],
            "https://github.com/django/django/blob/stable/6.0.x/"
            "django/forms/forms.py",
        )

    def test_sourcefile_supports_explicit_title(self):
        role_nodes, messages = self.sourcefile("'forms.py' <django/forms/forms.py>")

        self.assertEqual(messages, [])
        self.assertEqual(role_nodes[0].astext(), "'forms.py'")

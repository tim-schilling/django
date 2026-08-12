import pathlib
import sys
from types import SimpleNamespace
from unittest import SkipTest

from django.test import SimpleTestCase

# The import must happen at the end of setUpClass, so it can't be imported at
# the top of the file.
djangodocs = None


class DjangoDocsTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        # The file implementing the code under test is in the docs folder and
        # is not part of the Django package. This means it cannot be imported
        # through standard means. Include its parent in the pythonpath for the
        # duration of the tests to allow the code to be imported.
        cls.ext_path = str((pathlib.Path(__file__).parents[2] / "docs/_ext").resolve())
        sys.path.insert(0, cls.ext_path)
        cls.addClassCleanup(sys.path.remove, cls.ext_path)
        cls.addClassCleanup(sys.modules.pop, "djangodocs", None)
        cls.addClassCleanup(sys.modules.pop, "github_links", None)

        # The test package is named "sphinx", which shadows the Sphinx package
        # when the extension is imported.
        tests_path = str(pathlib.Path(__file__).parents[1].resolve())
        sys.path.remove(tests_path)
        cls.addClassCleanup(sys.path.insert, 0, tests_path)
        test_package = sys.modules.pop("sphinx", None)
        if test_package is not None:
            cls.addClassCleanup(sys.modules.__setitem__, "sphinx", test_package)

        # Linters/IDEs may not be able to detect this as a valid import.
        try:
            import djangodocs as _djangodocs
        except ModuleNotFoundError as exc:
            if exc.name == "sphinx":
                raise SkipTest("Sphinx is not installed.") from exc
            raise

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

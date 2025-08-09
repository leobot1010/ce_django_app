from django.test import TestCase
from unittest.mock import patch
from ce.utils.scheme_utils import generate_app_code


class SchemeUtilsTests(TestCase):
    @patch("utils.scheme_utils.Scheme.objects.filter")
    def test_generate_app_code(self, mock_filter):
        mock_filter.return_value.count.return_value = 4  # 4 existing schemes
        code = generate_app_code("Kerry")
        self.assertEqual(code, "KY005")


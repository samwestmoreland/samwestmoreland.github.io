import unittest
import converters.convert_errors_to_html as convert_errors_to_html

class TestConvertBackticksToHTML(unittest.TestCase):
    def test_one_pair(self):
        input = "here is some code: `print('hello world')`"
        expected_output = "here is some code: <code>print('hello world')</code>"
        self.assertEqual(convert_errors_to_html.render_code_tags_in_string(input), expected_output)

    def test_no_backticks(self):
        input = "no code here!"
        expected_output = "no code here!"
        self.assertEqual(convert_errors_to_html.render_code_tags_in_string(input), expected_output)

    def test_multiple_pairs(self):
        input = "here is some code: `print('hello world')`, `print('hello world')`"
        expected_output = "here is some code: <code>print('hello world')</code>, <code>print('hello world')</code>"
        self.assertEqual(convert_errors_to_html.render_code_tags_in_string(input), expected_output)

    def test_odd_set_of_backticks(self):
        input = "here is some code: `print('hello world')` `print('hello world')"
        expected_output = "here is some code: <code>print('hello world')</code> <code>print('hello world')"
        self.assertEqual(convert_errors_to_html.render_code_tags_in_string(input), expected_output)

    def test_convert_error_object(self):
        input = {
            "title": "my error",
            "context": "here is some code: `print('hello world')`",
            "explanation": "this happens because x, which you can see when you do `print('hello world')`",
            "solution": "simply run `foo`"
        }
        expected_output = {
            "title": "my error",
            "context": "here is some code: <code>print('hello world')</code>",
            "explanation": "this happens because x, which you can see when you do <code>print('hello world')</code>",
            "solution": "simply run <code>foo</code>"
        }

        actual_output = convert_errors_to_html.render_code_tags(input)

        for field in expected_output:
            self.assertEqual(actual_output[field], expected_output[field])


if __name__ == '__main__':
    unittest.main()

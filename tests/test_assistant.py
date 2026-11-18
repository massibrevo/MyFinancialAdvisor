import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock

from financewebapp.assistant import DEFAULT_MODEL, IncompleteResponse, stream_answer


def event(kind, delta=None):
    return SimpleNamespace(type=kind, delta=delta)


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.messages = [{"role": "user", "content": "Come funziona?"}]

    def test_streaming_configuration_and_selected_context(self):
        self.client.responses.create.return_value = nullcontext(iter([
            event("response.output_text.delta", "Una "),
            event("response.output_text.delta", "risposta"),
            event("response.completed"),
        ]))
        answer = "".join(stream_answer(self.client, DEFAULT_MODEL, self.messages, "Mutuo di esempio"))
        self.assertEqual(answer, "Una risposta")
        request = self.client.responses.create.call_args.kwargs
        self.assertEqual(request["input"], self.messages)
        self.assertIn("Mutuo di esempio", request["instructions"])
        self.assertIs(request["store"], False)
        self.assertIs(request["stream"], True)
        self.assertEqual(request["model"], DEFAULT_MODEL)

    def test_incomplete_stream_is_reported(self):
        self.client.responses.create.return_value = nullcontext(iter([
            event("response.output_text.delta", "Parziale"),
            event("response.incomplete"),
        ]))
        with self.assertRaises(IncompleteResponse):
            list(stream_answer(self.client, DEFAULT_MODEL, self.messages))

    def test_only_recent_messages_go_to_the_api(self):
        messages = [{"role": "user", "content": str(index)} for index in range(20)]
        self.client.responses.create.return_value = nullcontext(iter([event("response.completed")]))
        list(stream_answer(self.client, "configured-model", messages))
        request = self.client.responses.create.call_args.kwargs
        self.assertEqual(request["input"], messages[-12:])
        self.assertNotIn("reasoning", request)

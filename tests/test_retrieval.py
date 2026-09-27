from pathlib import Path
import tempfile
import unittest

from personal_wiki.retrieval import ingest, search
from personal_wiki.config import Config
from personal_wiki.harness import RunResult, WikiHarness


class RetrievalTests(unittest.TestCase):
    def test_reingestion_is_idempotent_and_updates_in_place(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = root / "notes"
            notes.mkdir()
            note = notes / "Clear Name.md"
            note.write_text("# Clear Name\n\nK-means alternates assignment and centroid updates.", encoding="utf-8")
            database = root / "index.sqlite3"

            first = ingest(notes, database)
            second = ingest(notes, database)
            self.assertEqual(first.indexed, 1)
            self.assertEqual(second.unchanged, 1)
            self.assertEqual(len(search(database, "centroid", 10)), 1)

            note.write_text("# Clear Name\n\nK-means uses centroids and repeated assignment.", encoding="utf-8")
            third = ingest(notes, database)
            self.assertEqual(third.indexed, 1)
            self.assertEqual(len(search(database, "centroid", 10)), 1)

    def test_removed_source_is_removed_from_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = root / "notes"
            notes.mkdir()
            note = notes / "Temporary.md"
            note.write_text("# Temporary\n\nUnique zephyr evidence.", encoding="utf-8")
            database = root / "index.sqlite3"
            ingest(notes, database)
            note.unlink()
            stats = ingest(notes, database)
            self.assertEqual(stats.removed, 1)
            self.assertEqual(search(database, "zephyr", 10), [])

    def test_ask_does_not_include_chat_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompts = root / "prompts"
            prompts.mkdir()
            (prompts / "assistant.md").write_text("assistant", encoding="utf-8")
            (prompts / "research.md").write_text("research", encoding="utf-8")
            note = root / "Evidence.md"
            note.write_text("# Evidence\n\nK-means updates each centroid using a mean.", encoding="utf-8")
            config = Config(root, root, root, root / "data")
            ingest(note, config.database)
            harness = WikiHarness(config)
            harness.chat_history = [
                {"role": "user", "content": "SECRET CHAT MARKER"},
                {"role": "assistant", "content": "remembered"},
            ]
            captured = {}

            def fake_generate(messages, **kwargs):
                captured["messages"] = messages
                return "The centroid uses a mean [1]."

            harness.model.generate = fake_generate
            result = harness.ask("How is a K-means centroid updated?")
            rendered = str(captured["messages"])
            self.assertNotIn("SECRET CHAT MARKER", rendered)
            self.assertIn("research", rendered)
            self.assertIn("[1]", result.answer)

    def test_navigation_is_not_evidence_and_search_can_require_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            (vault / "raw").mkdir(parents=True)
            (vault / "wiki").mkdir()
            (vault / "index.md").write_text(
                "# Index\n\nRetrieval and ranking navigation.", encoding="utf-8"
            )
            (vault / "raw" / "Course.md").write_text(
                "# Course\n\nRetrieval gathers candidates and ranking orders them.", encoding="utf-8"
            )
            (vault / "wiki" / "Recommenders.md").write_text(
                "# Recommenders\n\nRetrieval and ranking form a pipeline.", encoding="utf-8"
            )
            database = root / "index.sqlite3"
            ingest(vault, database)

            evidence = search(database, "retrieval ranking", 10)
            originals = search(database, "retrieval ranking", 10, original_only=True)
            self.assertNotIn("index.md", [item.path for item in evidence])
            self.assertEqual([item.path for item in originals], ["raw/Course.md"])

    def test_chat_retrieval_is_selective(self):
        self.assertFalse(WikiHarness._chat_needs_wiki("Draft a short thank-you email."))
        self.assertTrue(WikiHarness._chat_needs_wiki("What do my notes say about K-means?"))
        self.assertEqual(
            WikiHarness._chat_retrieval_query(
                "What do my notes say about how K-means updates centroids?"
            ),
            "how K-means updates centroids",
        )

    def test_saved_runs_have_unique_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = Config(root, root, root, root / "data")
            harness = WikiHarness(config)
            result = RunResult("ask", "question", "answer", [], 0.01)
            first = harness.save(result)
            second = harness.save(result)
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())



    def test_wiki_backed_chat_retries_when_citations_are_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompts = root / "prompts"
            prompts.mkdir()
            (prompts / "assistant.md").write_text(
                "Cite factual claims from wiki evidence.", encoding="utf-8"
            )
            (prompts / "research.md").write_text("Research rules.", encoding="utf-8")
            note = root / "Evidence.md"
            note.write_text(
                "# Evidence\n\nK-means updates centroids using the assigned-point mean.",
                encoding="utf-8",
            )
            config = Config(root, root, root, root / "data")
            ingest(note, config.database)
            harness = WikiHarness(config)

            responses = iter([
                "K-means updates centroids using the assigned-point mean.",
                "K-means updates centroids using the assigned-point mean [1].",
            ])
            calls = []

            def fake_generate(messages, **kwargs):
                calls.append(messages)
                return next(responses)

            harness.model.generate = fake_generate
            result = harness.chat(
                "What do my notes say about K-means centroids?"
            )

            self.assertEqual(len(calls), 2)
            self.assertEqual(len(result.passages), 1)
            self.assertIn("[1]", result.answer)
if __name__ == "__main__":
    unittest.main()

"""배포 스크립트의 실제 입출력과 경로·그래프 회귀를 검증한다."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/unobsidian/scripts"


class ReleaseTests(unittest.TestCase):
    """격리한 샘플 보관함으로 다섯 명령의 배포 동작을 검증한다."""

    def setUp(self):
        """상호 참조·임베드·태그·Canvas가 있는 보관함을 준비한다."""
        self.temp = tempfile.TemporaryDirectory(prefix="unobsidian ", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name) / "vault & notes"
        self.vault.mkdir()
        notes = {
            "A.md": (
                "---\ntags: [frontmatter]\n---\n"
                "[[B]]\n![[B]]\n#project/frontend\n"
                "`[[Ignored]]`\n```\n[[Ignored2]]\n```\n"
            ),
            "B.md": "[[A]]\n[[C]]\n#project/backend\n#project/frontend\n",
            "C.md": "#other\n",
            "한글 노트.md": "[[A]]\n",
            "Isolated.md": "No links here.\n",
            "Board.canvas": '{"nodes": [], "edges": []}',
        }
        for name in notes:
            (self.vault / name).write_text(notes[name], encoding="utf-8")

    def run_command(self, script, *args):
        """현재 Python으로 명령을 실행하고 UTF-8 출력을 수집한다."""
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), "--vault", str(self.vault), *args],
            capture_output=True, text=True, encoding="utf-8", env=env,
        )

    def test_graph_formats_and_syntax(self):
        """기본 텍스트·D3 JSON과 코드 제외·프런트매터 태그를 검증한다."""
        text = self.run_command("get_graph.py")
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn('"한글 노트": A', text.stdout)
        result = self.run_command("get_graph.py", "--format", "d3")
        self.assertEqual(result.returncode, 0, result.stderr)
        graph = json.loads(result.stdout)
        ids = set()
        for node in graph["nodes"]:
            ids.add(node["id"])
        self.assertIn("#frontmatter", ids)
        self.assertIn("Board.canvas", ids)
        self.assertNotIn("Ignored", ids)
        self.assertNotIn("Ignored2", ids)

    def test_neighbors_preserve_directions_and_relations(self):
        """반경 안의 모든 링크를 원래 방향·관계·순서로 보존한다."""
        full = json.loads(self.run_command("get_graph.py", "--format", "d3").stdout)
        result = self.run_command("get_neighbors.py", "--node", "A", "--format", "d3")
        self.assertEqual(result.returncode, 0, result.stderr)
        graph = json.loads(result.stdout)
        ids = set()
        for node in graph["nodes"]:
            ids.add(node["id"])
        expected = []
        for link in full["links"]:
            if link["source"] in ids and link["target"] in ids:
                expected.append(link)
        self.assertEqual(graph["links"], expected)
        self.assertNotIn("C", ids)
        again = self.run_command("get_neighbors.py", "--node", "A", "--format", "d3")
        self.assertEqual(json.loads(again.stdout), graph)

    def test_isolated_node_and_depth(self):
        """고립 노드와 두 단계 이웃 탐색을 검증한다."""
        isolated = self.run_command("get_neighbors.py", "--node", "Isolated", "--format", "d3")
        graph = json.loads(isolated.stdout)
        self.assertEqual(graph, {"nodes": [{"id": "Isolated", "type": "file"}], "links": []})
        result = self.run_command("get_neighbors.py", "--node", "A", "--depth", "2", "--format", "d3")
        ids = []
        for node in json.loads(result.stdout)["nodes"]:
            ids.append(node["id"])
        self.assertIn("C", ids)

    def test_tag_with_or_without_hash(self):
        """샵 접두사 유무와 관계없이 하위 태그 노트를 찾는다."""
        plain = self.run_command("search_by_tag.py", "--tag", "project")
        hashed = self.run_command("search_by_tag.py", "--tag", "#project")
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(hashed.returncode, 0, hashed.stderr)
        self.assertEqual(json.loads(plain.stdout), json.loads(hashed.stdout))
        self.assertEqual(json.loads(plain.stdout)["count"], 2)

    def test_resolve_relative_vault_and_canvas(self):
        """상대 보관함에서도 절대경로를 반환하고 Canvas 확장자를 유지한다."""
        self.vault = Path(os.path.relpath(self.vault))
        filenames = {"A": "A.md", "Board.canvas": "Board.canvas"}
        for file_id in filenames:
            result = self.run_command("resolve_filepath.py", "--file-id", file_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = Path(json.loads(result.stdout)["path"])
            self.assertTrue(actual.is_absolute())
            self.assertEqual(actual, (self.vault / filenames[file_id]).resolve())

    def test_visualize_relative_output(self):
        """상대 출력 경로로 생성한 파일을 절대 URI로 브라우저에 전달한다."""
        spec = importlib.util.spec_from_file_location("visualize", SCRIPTS / "visualize_graph.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = Path(os.path.relpath(Path(self.temp.name) / "graph.html"))
        args = ["visualize_graph.py", "--vault", str(self.vault), "--output", str(output)]
        with patch.object(sys, "argv", args), patch.object(module.webbrowser, "open") as browser:
            module.main()
        browser.assert_called_once_with(output.resolve().as_uri())
        html = output.read_text(encoding="utf-8")
        self.assertIn("vault &amp; notes", html)

    def test_visualization_embedded_data_cannot_end_script(self):
        """노트 연결 문자열이 HTML의 script 요소를 종료하지 못하게 한다."""
        spec = importlib.util.spec_from_file_location("visualize", SCRIPTS / "visualize_graph.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        payload = "</script><script>window.injected=true</script>"
        graph = {"nodes": [{"id": payload, "label": payload, "type": "file"}], "links": []}
        output = Path(self.temp.name) / "safe.html"
        args = ["visualize_graph.py", "--vault", str(self.vault), "--output", str(output), "--no-open"]
        with patch.object(sys, "argv", args), patch.object(module, "results_to_d3", return_value=graph):
            module.main()
        html = output.read_text(encoding="utf-8")
        self.assertNotIn(payload, html)
        data = html.split("const graph = ", 1)[1].split(";\n", 1)[0]
        self.assertEqual(json.loads(data), graph)

    def test_invalid_depth_is_rejected(self):
        """지원 범위를 벗어난 탐색 깊이를 변경하지 않고 오류로 처리한다."""
        for depth in ("0", "4"):
            result = self.run_command("get_neighbors.py", "--node", "A", "--depth", depth)
            self.assertNotEqual(result.returncode, 0)

    def test_empty_tag_is_rejected(self):
        """태그가 없거나 샵 기호만 있으면 입력 오류를 반환한다."""
        for tag in ("", "#"):
            result = self.run_command("search_by_tag.py", "--tag", tag)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("error", json.loads(result.stderr))

    def test_missing_inputs_report_errors(self):
        """존재하지 않는 노드·파일·보관함을 오류로 처리한다."""
        commands = {
            "get_neighbors.py": ["--node", "Missing"],
            "resolve_filepath.py": ["--file-id", "Missing"],
        }
        for script in commands:
            result = self.run_command(script, *commands[script])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("error", json.loads(result.stderr))
        self.vault = self.vault / "does-not-exist"
        result = self.run_command("get_graph.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", json.loads(result.stderr))


if __name__ == "__main__":
    unittest.main()
